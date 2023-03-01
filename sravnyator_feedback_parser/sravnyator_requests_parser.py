import csv
import re
from time import sleep
from typing import Optional
from bs4 import BeautifulSoup
from bs4.element import Tag

from base_func.api_skillhub import get_schools_list
from base_func.date_tools import convert_to_date
from base_func.http_requests import fetch_html, send_feedbacks_data
from settings.logger_settings import logger

BASE_SOURCE_URL = 'https://journal.tinkoff.ru/sravnyator/courses/'


def run_sravnytor_parser():
    """ Находит список ссылок на данные о школах """
    main_page = fetch_html(BASE_SOURCE_URL)
    if main_page:
        soup = BeautifulSoup(main_page.content, 'lxml')
        school_elements = soup.select('div.schoolLinkContainer--vzJE2 a')
        school_urls = {}
        for element in school_elements:
            school_urls[re.split(r'\d', element.get_text())[0]] = 'https://journal.tinkoff.ru' + element.get('href')
        logger.debug(school_urls)

        schools_data = get_schools_list()
        for school in schools_data:
            for name, url in school_urls.items():
                if school['name'] in name:
                    get_school_reviews(school, url)


def get_school_reviews(shcool_data: dict, url: str):
    """ Собирает отзывы о школе с переданной страницы """
    main_page = fetch_html(url)
    if main_page:
        soup = BeautifulSoup(main_page.content, 'lxml')
        review_elements = soup.select('div.root--rXPGJ>div.root--V3bso.root--JOz8F')
        for item in review_elements:
            text_blocks = item.select('div.content--tbkyT div.block--HMisa')[::-1]
            text_blocks = [element.get_text() for element in text_blocks]
            h3_blocks = item.select('div.content--tbkyT h3')[::-1]
            h3_blocks = [element.get_text() for element in h3_blocks]
            description = text_blocks.pop()
            # удаляем переносы строк
            description = " ".join(description.splitlines())
            feedback_plus = None
            feedback_minus = None
            for number, block in enumerate(h3_blocks):
                if block == 'Достоинства':
                    feedback_plus = text_blocks[number]
                    feedback_plus = " ".join(feedback_plus.splitlines())
                elif block == 'Недостатки':
                    feedback_minus = text_blocks[number]
                    feedback_minus = " ".join(feedback_minus.splitlines())
            feedback_date = find_feedback_date(item)
            rating = find_feedback_rating(item)
            feedback_review = {
                'school': shcool_data['name'],
                'feedback_source': BASE_SOURCE_URL,
                'feedback_url': url,
                'feedback_plus': feedback_plus,
                'feedback_minus': feedback_minus,
                'feedback_description': description,
                'feedback_date': feedback_date,
                'rating': rating,
            }
            write_data(feedback_review.values())
            # send_feedbacks_data(feedback_review)
    else:
        logger.warning(f'Не получилось загрузить страницу url={url}')
    sleep(20)


def find_feedback_date(feedback_element: Tag) -> Optional[str]:
    """ Находит в данные о дате отзыва """
    feedback_date = feedback_element.select_one('div.date--ego3w')
    try:
        feedback_date = feedback_date.get_text()
        # ожидаемый формат полученных данных: "10.11.2022"
        feedback_date = feedback_date.split('T')[0]
        feedback_date = str(convert_to_date(feedback_date))
    except ValueError:
        feedback_date = None
    return feedback_date


def find_feedback_rating(feedback_element: Tag) -> Optional[float]:
    """ Находит в данные о рейтинге отзыва """
    raiting_stars_elements = feedback_element.select('svg.star--C5zl8.star--MJWDi .highlightFill--HLIU6')
    raiting_star = int(len(raiting_stars_elements))
    return raiting_star

def write_data(data):
    with open('sravnytor.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(data)
