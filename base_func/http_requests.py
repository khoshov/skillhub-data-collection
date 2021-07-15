import json
import os
from typing import Dict

import requests
import requests_random_user_agent  # noqa
from dotenv import load_dotenv

from settings.logger_settings import logger

load_dotenv()


@logger.catch
def fetch_html(url: str) -> str:
    """ функция получения данных с html страницы """
    try:
        result = requests.get(url, timeout=10)
        if result.status_code == 200:
            logger.info(f"парсинг ссылки {url}")
            return result.text
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
        'Api-Key': os.getenv("SKILLHUB_API_KEY"),
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
