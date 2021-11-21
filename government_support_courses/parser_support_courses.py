import json
import re
from time import sleep
from typing import Dict

from bs4 import BeautifulSoup

from base_func.http_requests import fetch_html, send_parse_data
from base_func.date_tools import convert_to_date
from base_func.mappings import gouverment_couts_category_mapping
from settings.logger_settings import logger
from settings.mapping import COURSE_DURATION_TYPE


def parse_supported_courses(url):
    """Upload main courses data from API"""
    main_page_data = fetch_html(url)
    products = main_page_data.json().get('products')
    if products:
        for product in products:
            course_data = {
                "school": product.get('descr').replace('&nbsp;', ' '),
                "course_title": product.get('title'),
                "course_price": int(product.get('price').split('.')[0]),
                "course_duration_type": COURSE_DURATION_TYPE['HOUR'],
                "government_support": True,
                "course_category": gouverment_couts_category_mapping(product.get('title'))
            }
            course_description = load_course_description(product.get('url'))
            if not course_description:
                logger.warning(f'Not active course {product.get("url")}')
                continue
            course_data.update(course_description)
            send_parse_data(course_data)
            sleep(15)


def load_course_description(course_description_url: str) -> Dict:
    """Upload course description from page"""
    course_is_active = False
    course_page = fetch_html(course_description_url)
    if course_page:
        course_description = {}
        soup_course_page = BeautifulSoup(course_page.text, 'lxml')
        # находим ссылку на страницу курса
        course_url = soup_course_page.select_one('.js-store-prod-all-text a')
        if course_url:
            course_url = course_url.get('href')
            course_description['course_link'] = course_url.split('?utm')[0]
        # find course description
        description = soup_course_page.select('.js-store-prod-all-text strong')
        description = [item.get_text() for item in description]
        if len(description) < 5:
            logger.warning(f'There is little data in the course description {course_description_url}')
            return {}
        # find course start date and duration
        course_duration = re.search(r'\s(\d+?)\s', description.pop())
        if course_duration:
            course_description['course_duration'] = course_duration.group(1)
            course_description['course_duration_type'] = COURSE_DURATION_TYPE.get("HOUR")
        for element in description[3:]:
            if 'закрыт' in element:
                continue
            course_dates_block = re.search(r'(\d{2}.\d{2}.\d{2,4}).+?(\d{2}.\d{2}.\d{2,4})', element)
            if course_dates_block:
                course_description['course_start_date'] = str(convert_to_date(course_dates_block.group(1)))
                course_is_active = True
                break

        if course_is_active:
            return course_description

    return {}
