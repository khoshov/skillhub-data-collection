""" Файл содержит логику прасинга отзывов через API 2gis """
from datetime import datetime
from typing import Dict, List, Optional

from dateutil import tz
from dateutil.parser import parse
import requests
from user_agent import generate_user_agent

from base_func.api_skillhub import get_schools_list
from base_func.http_requests import send_feedbacks_data
from settings.logger_settings import logger


SUGGESTS_KEY = 'rurbbn3446'
SUGGESTS_URL = 'https://catalog.api.2gis.ru/3.0/suggests'
REVIEWS_KEY = '37c04fe6-a560-4549-b459-02309cf643ad'
REVIEWS_URL_TEMPLATE = 'https://public-api.reviews.2gis.com/2.0/branches/{school_id}/reviews'
TZ = tz.gettz('Asia/Novosibirsk')


def get_school_id(school_name: str) -> Optional[int]:
    """
    Получает данные о школе по названию через API
    https://docs.2gis.com/ru/api/search/suggest/reference/3.0/suggests
    """
    headers = {
        'User-Agent': generate_user_agent(),
    }
    params = {
        'key': SUGGESTS_KEY,
        'q': school_name,
        'viewpoint1': '24.945611304013696,63.57433046702851',
        'viewpoint2': '50.10704576027874,48.3575978301023',
        'locale': 'ru_RU',
    }
    response = requests.get(SUGGESTS_URL, params=params, headers=headers)
    json_data = response.json()
    if json_data.get('meta').get('code') == 200:
        for item in json_data['result']['items']:
            if is_correct_school_name(school_name, item):
                return item.get('id')

    logger.info(f'Компания {school_name} не найдена на 2gis.ru')
    return None


def get_school_reviews(school_id: int) -> List[Dict]:
    """ Получаем отзывы о школе по id через API """
    url = REVIEWS_URL_TEMPLATE.format(school_id=school_id)
    now = datetime.now(tz=TZ).isoformat()
    params = {
        'limit': '50',
        'offset_date': now,
        'rated': 'true',
        'sort_by': 'date_edited',
        'key': REVIEWS_KEY,
    }
    all_reviews = []
    has_more_reviews = True
    while has_more_reviews:
        response = requests.get(url, params=params)
        json_data = response.json()
        reviews = json_data.get('reviews', [])
        last_review = reviews[-1] if reviews else {}
        last_review_created = last_review.get('date_created')
        if not last_review_created:
            has_more_reviews = False
        else:
            all_reviews.extend(reviews)
            params['offset_date'] = last_review_created
    return all_reviews


def is_correct_school_name(school_name: str, item: Dict) -> bool:
    """
    проверяет совпадение название найденного объекта со входящими данными
    ToDo: после обновления API skillhub переделать функцию
    """
    if school_name in item.get('name'):
        return True
    return False


def run_2gis_parser():
    schools_data = get_schools_list()

    for school in schools_data:
        school_id = get_school_id(school.get('name'))
        reviews = get_school_reviews(school_id)

        for review in reviews:
            description = " ".join(review.get('text').splitlines())
            review = {
                'school': school.get('name'),
                'feedback_source': '2gis.ru',
                'feedback_url': REVIEWS_URL_TEMPLATE.format(school_id=school_id),
                'feedback_description': description,
                'feedback_date': str(parse(review.get('date_created')).date()),
                'rating': review.get('rating'),
            }
            send_feedbacks_data(review)
