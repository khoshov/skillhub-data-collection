import json
import os
from itertools import cycle
from random import randint
from time import sleep
from typing import Dict

import cloudscraper
import requests
from dotenv import load_dotenv

from settings.browser_config import USER_AGENT
from settings.logger_settings import logger


load_dotenv()


PROXIES = [
    "http://102.129.249.120:8080",
]

INTERPRETER_GENERATOR = cycle(['chakracore', 'js2py', 'native', 'nodejs', 'v8'])


@logger.catch
def fetch_html(url: str) -> requests.models.Response:
    """ функция получения данных с html страницы """
    sleep(randint(1, 5))  # пауза между запросами
    try:
        headers = {
            'user-agent': USER_AGENT,
            'accept-encoding': 'gzip',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        # proxy = choice(PROXIES)
        # proxies = {
        #     "http": f"{proxy}",
        #     "https": f"{proxy}"
        # }
        result = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        # result = requests.get(url, allow_redirects=True, timeout=10)
        if result.status_code == 200:
            logger.info(f"{url} - ссылка доступна")
            return result
        else:
            logger.error(f'Ссылка {url} недоступна, status code {result.status_code}')
            return None
    except(requests.RequestException):
        logger.error(f'Страница не доступна url={url}, проверьте интернет соединение')
        return None


def create_cloudflare_scrapper():
    """создает scrapper с настройками для парсинга сайтов с защитой cloudflare

    Returns:
        _type_: _description_
    """
    # proxy = choice(PROXIES)
    # proxies = {
    #     "http": f"{proxy}",
    #     "https": f"{proxy}"
    # }
    # interpreter = next(INTERPRETER_GENERATOR)
    # logger.info(f"interpreter {interpreter}")
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'android',
            # 'mobile': False,
            'desktop': False,
        },
        # delay=10,
        # interpreter=interpreter
    )

    # scraper = cloudscraper.CloudScraper(
    #     browser='chrome',
    #     # platform='android',
    #     # desktop=False,
    #     interpreter=next(INTERPRETER_GENERATOR)
    # )
    return scraper

@logger.catch
def fetch_html_with_cloudflare(scraper, url: str) -> requests.models.Response:
    """ функция получения данных с html страницы с защитой cloudflare """
    try:
        # sleep(randint(15, 30))
        result = scraper.get(url)
        if result.status_code == 200:
            logger.info(f"парсинг ссылки {url}")
            return result
        elif result.status_code == 521:
            logger.error(f'Попытка получения данных по ссылке {url} заблокировано, status code {result.status_code}')
            return None
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
            logger.error(f'При направлении данных возникла ошибка: {result.status_code}. \n'
                         f'Описание ошибки {result.json()} \n'
                         f'Направляемые данные {feedbacks_data}')
    except requests.RequestException as e:
        logger.error(f'Отсутствует доступ к API: {e}')
