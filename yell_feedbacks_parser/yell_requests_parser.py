import csv
import json
from typing import Optional

from bs4 import BeautifulSoup as bs
from bs4.element import Tag
from yarl import URL

from base_func.api_skillhub import get_schools_list
from base_func.date_tools import convert_to_date
from base_func.http_requests import fetch_html, send_feedbacks_data
from settings.logger_settings import logger


BASE_SOURCE_URL = URL('https://www.yell.ru/')
SEARCH_URL = (BASE_SOURCE_URL / 'moscow/top/').human_repr()

BASE_TARGET_URL = URL('http://127.0.0.1:8000')
SCHOOLS_LIST_URL = (BASE_TARGET_URL / 'schools/').human_repr()


def run_yell_parser():
    """ Запускает сбор данных с yell.ru """
    logger.info("Парсер отзывов с yell.ru начал работу")
    schools_data = get_schools_list()
    school_names = [school['name'] for school in schools_data]
    for school in school_names:
        school_reviews_url = get_school_reviews_url(school)
        if school_reviews_url:
            get_school_reviews(school_reviews_url, school)
        else:
            logger.info(f"На сайте yell.ru отсутствуют данные о школе {school}")
    logger.info("Парсер отзывов с yell.ru закончил работу")


def get_school_reviews_url(school_name: str) -> Optional[str]:
    """
    Находит ссылку с информацией о компании и на ее основе генерирует ссылку на страницу с отзывами
    """
    logger.info(f'{SEARCH_URL}?text={school_name}')
    response = fetch_html(f'{SEARCH_URL}?text={school_name}')
    soup = bs(response.content, 'lxml')

    if href_element := soup.select_one('h2 a.companies__item-title-text'):
        title = href_element.get_text()
        # проверяем входит ли название школы в загаловок
        if school_name.lower() in title.lower():
            url = href_element.get('href')
            return (BASE_SOURCE_URL / url.lstrip('/') / 'reviews/').human_repr()
    return None


def get_school_reviews(school_reviews_url: str, school_name: str):
    """ Собирает отзывы о школе с переданной страницы """
    response = fetch_html(school_reviews_url)
    if response:
        soup = bs(response.content, 'lxml')
        items = soup.select('div.reviews__item')
        for item in items:
            data = json.loads(item.get('data-review'))
            description = data.get('text').strip()
            # удаляем переносы строк
            description = " ".join(description.splitlines())
            feedback_date = find_feedback_date(item)
            rating = find_feedback_rating(item)
            feedback_review = {
                'school': school_name,
                'feedback_source': BASE_SOURCE_URL,
                'feedback_url': school_reviews_url,
                'feedback_description': description,
                'feedback_date': feedback_date,
                'rating': rating,
            }
            # write_data(feedback_review.values())
            send_feedbacks_data(feedback_review)
    else:
        logger.info(f"На сайте yell.ru отсутствуют отзывы о школе {school_name}")

def find_feedback_date(feedback_element: Tag) -> Optional[str]:
    """ Находит в данные о дате отзыва """
    feedback_date = feedback_element.select_one('span.reviews__item-added')
    try:
        feedback_date = feedback_date.get('content')
        # формат полученных данных: "2020-02-14T12:42:54+0300"
        feedback_date = feedback_date.split('T')[0]
        feedback_date = str(convert_to_date(feedback_date))
    except ValueError:
        feedback_date = None
    return feedback_date


def find_feedback_rating(feedback_element: Tag) -> Optional[float]:
    """ Находит в данные о рейтинге отзыва """
    raiting_stars_element = feedback_element.select_one('span.rating__value')
    raiting_star = int(raiting_stars_element.get_text())
    return raiting_star


def write_data(data):
    with open('yell_data.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(data)
