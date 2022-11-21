""" Парсер отзывов с сайте mooc.ru через requests """

import csv
from typing import Optional

from bs4 import BeautifulSoup
from bs4.element import Tag

from base_func.api_skillhub import get_schools_list
from base_func.date_tools import convert_to_date
from base_func.http_requests import fetch_html, send_feedbacks_data
from settings.logger_settings import logger


BASE_SOURCE_URL = 'https://mooc.ru/'
MAIN_COMPANY_LIST = 'https://mooc.ru/companies'


def run_mooc_parser():
    """
    Получает из API SkillHub список школ, находит необходимые ссылки на отзывы о школе на mooc.ru
    """
    schools_data = get_schools_list()
    load_main_company = fetch_html(MAIN_COMPANY_LIST)
    main_company_soup = BeautifulSoup(load_main_company.text, 'lxml')
    company_names = [item.get_text().strip(' \n') for item in main_company_soup.select('div.card .ml-5') if item]
    company_reviews_links = [item.get('href') for item in main_company_soup.select('div.card .ml-3') if item]
    # преобразуем ссылки в абсолютные
    company_reviews_links = [(BASE_SOURCE_URL + item.lstrip('/')) for item in company_reviews_links]
    # объединяем данные в словарь
    company_reviews_link_data = dict(zip(company_names, company_reviews_links))
    for element in schools_data:
        for key, url in company_reviews_link_data.items():
            if element.get('name') in key:
                collect_school_feedbacks(url, element)
                break


def collect_school_feedbacks(url: str, school_data):
    """ собирает заявки о школе по данной ссылке """
    next_page = url
    school_name = school_data.get('name')
    logger.info(f"Старт сборы отзывов о школе {school_name}")
    while next_page:
        logger.info(f'next page = {next_page}')
        main_reviews_page = fetch_html(next_page)
        main_reviews_page_soup = BeautifulSoup(main_reviews_page.text, 'lxml')
        reviews_data = main_reviews_page_soup.select('.feedback .ReviewItem > .descr')
        for element in reviews_data:
            feedback_date = find_feedback_date(element)
            description = element.select_one('.text').get_text().strip()
            # удаляем переносы строк
            description = " ".join(description.splitlines())
            rating = find_feedback_rating(element)

            feedback_review = {
                'school': school_name,
                'feedback_source': 'https://mooc.com/',
                'feedback_url': url,
                'feedback_description': description,
                'feedback_date': feedback_date,
                'rating': rating,
            }
            # пропускаем отправку данных если нет обязательных полей
            if not feedback_date or not description:
                continue
            send_feedbacks_data(feedback_review)

        next_page = main_reviews_page_soup.select_one('.basic-pagination .next a')
        if next_page:
            next_page = next_page.get('href')
            next_page = (BASE_SOURCE_URL + next_page.lstrip('/'))
        else:
            next_page = None
            logger.info(f"Сборы отзывов о школе {school_name} завершен")


def find_feedback_date(feedback_element: Tag) -> Optional[str]:
    """ Находит в данные о дате отзыва """
    feedback_date = feedback_element.select('.info span.ml-4.mr-3')
    if len(feedback_date) >= 1:
        try:
            feedback_date = feedback_date[0].get_text()
            feedback_date = feedback_date.split()[-1]
            feedback_date = str(convert_to_date(feedback_date))
        except ValueError:
            feedback_date = None
    else:
        feedback_date = None
    return feedback_date


def find_feedback_rating(feedback_element: Tag) -> Optional[float]:
    """ Находит в данные о рейтинге отзыва """
    raiting_stars = feedback_element.select_one('.rating')
    if len(raiting_stars.select('i.fas')) == 0:
        rating = 0
    else:
        rating = len(raiting_stars.select('i.fas.fa-star'))
    return int(rating)
