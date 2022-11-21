""" Содержит функции для взаимодействия с API SkillHub """
import json
import os
from typing import Optional

from base_func.http_requests import fetch_html

def get_schools_list() -> Optional[dict]:
    """ Получаем список школ и дату последенго отзыва, записанного в базе """
    response = fetch_html(os.getenv('SKILLHUB_GET_SCHOOLS')).json()
    if response:
        return response.get('results')
    return None
