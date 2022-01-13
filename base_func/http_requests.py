import json
from random import choice
import os
from typing import Dict, Optional

import requests
from fake_useragent import UserAgent
from dotenv import load_dotenv

from settings.logger_settings import logger


load_dotenv()
ua = UserAgent(verify_ssl=False)

PROXIES = [
    "http://102.129.249.120:8080",
]


@logger.catch
def fetch_html(url: str) -> requests.models.Response:
    """ функция получения данных с html страницы """
    try:
        headers = {
            'user-agent': ua.random,
            'Accept': 'text/html',
            'accept-encoding': 'gzip',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        # proxy = choice(PROXIES)
        # proxies = {
        #     "http": f"{proxy}",
        #     "https": f"{proxy}"
        # }
        result = requests.get(url, headers=headers, timeout=10)
        if result.status_code == 200:
            logger.info(f"парсинг ссылки {url}")
            return result
        else:
            logger.error(f'Ссылка {url} недоступна, status code {result.status_code}')
            return None
    except(requests.RequestException):
        logger.error(f'Страница не доступна url={url}, проверьте интернет соединение')
        return None


@logger.catch
def send_parse_data(course_data: Dict) -> None:
    """ функция направляет данные о курсе на Django сервер """

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
        'Accept-Encoding': 'deflate',
        'Authorization': f'Api-Key {os.getenv("DJANGO_SERVER_API_KEY")}'
    }

    data = json.dumps(course_data, ensure_ascii=False).encode('utf-8')
    try:
        result = requests.post(os.getenv("DJANGO_SERVER_URL"), headers=headers, data=data)
        if result.status_code == 201:
            logger.info(f"Данные {course_data.get('course_title')} успешно направлены")
        else:
            logger.error(f'При направлении данных возникла ошибка: {result.status_code}')
    except requests.RequestException as e:
        logger.error(f'Отсутствует доступ к API: {e}')


@logger.catch
def send_feedbacks_data(feedbacks_data: Dict) -> None:
    """ функция направляет данные об отзывах на Django сервер """

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
        'Accept-Encoding': 'deflate',
        'Authorization': f'Api-Key {os.getenv("DJANGO_SERVER_API_KEY")}'
    }

    data = json.dumps(feedbacks_data, ensure_ascii=False).encode('utf-8')
    try:
        result = requests.post(os.getenv("DJANGO_REVIEWS_URL"), headers=headers, data=data)
        if result.status_code == 201:
            logger.info(f"Отзыв о школе {feedbacks_data.get('school')} "
                        f"url={feedbacks_data.get('feedback_url')} успешно направлены в API")
        else:
            logger.error(f'При направлении данных возникла ошибка: {result.status_code}')
    except requests.RequestException as e:
        logger.error(f'Отсутствует доступ к API: {e}')
