import csv
from time import sleep
from typing import List, Dict

from bs4 import BeautifulSoup

from base_func.http_requests import fetch_html, send_parse_data
from base_func.utils import convert_to_date


SCHOOL = "geekbrains.ru"


def find_school_feedback_urls(url: str) -> BeautifulSoup:
    """получаем данные поискового get-запроса на главную страницу отзовик.ру"""
    search_request = fetch_html(url).text
    return BeautifulSoup(search_request, 'lxml')


def choose_most_popular_url(search_page_soup_data: BeautifulSoup) -> str:
    """парсинг полученных данных с целью поиска наиболее релевантной ссылки на список отзывов"""
    item_sortable_list = search_page_soup_data.select(".item.sortable")
    # удаляем рекламные ссылки
    item_sortable_list = [item for item in item_sortable_list if item["data-reviews"] != "0"]
    # берем первую самую популярную ссылку из найденных
    most_popular_feedbacks_url = 'https://otzovik.com' + item_sortable_list[0].select_one('h3 a')['href']
    most_popular_feedbacks_url = most_popular_feedbacks_url + '?order=date_desc'
    return most_popular_feedbacks_url


def collect_school_feedbacks_url(most_popular_feedbacks_url: str) -> List:
    """переход на ссылку с отзывами о курсе"""
    school_feedbacks_page = fetch_html(most_popular_feedbacks_url).text
    school_page_soup_data = BeautifulSoup(school_feedbacks_page, 'lxml')
    # ищем ссылки непосредственно на отзывы
    school_feedbacks_url_list = [
        'https://otzovik.com' + item['href'] for item in school_page_soup_data.select(".review-title")
    ]
    next_page = school_page_soup_data.find('a.next')
    if next_page:
        next_page = 'https://otzovik.com' + next_page['href']
    else:
        next_page = None
    return school_feedbacks_url_list, next_page


def fetch_feedback_data(url: str) -> Dict:
    """получили данные с отзывами по конкретной ccылке"""
    feedback_page = fetch_html(url).text
    feedback_page_soup_data = BeautifulSoup(feedback_page, 'lxml')
    feedback_plus = feedback_page_soup_data.select_one(".review-plus").get_text()
    feedback_minus = feedback_page_soup_data.select_one(".review-minus").get_text()
    feedback_description = feedback_page_soup_data.select_one(".review-body.description").get_text()
    feedback_description = feedback_description.replace('\n', ' ')
    feedback_date = feedback_page_soup_data.select_one(".review-postdate .tooltip-right").get_text()
    feedback_data = {
        'school': SCHOOL,
        'feedback_source': 'https://otzovik.com/',
        'feedback_url': url,
        'feedback_plus': feedback_plus,
        'feedback_minus': feedback_minus,
        'feedback_description': feedback_description,
        'feedback_date': convert_to_date(feedback_date),
    }
    return feedback_data


def run_feedbacks_parser(query: str = "geekbrains.ru"):
    """запуск парсинга отзывов и направление результатов во внешний API"""
    url_search = f"https://otzovik.com/?search_text={query}&x=0&y=0"
    next_page = choose_most_popular_url(find_school_feedback_urls(url_search))
    sleep(10)
    with open('feedbacks_data.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        head = [
            'school',
            'feedback_source',
            'feedback_url',
            'feedback_plus',
            'feedback_minus',
            'feedback_description',
            'feedback_date'
        ]
        writer.writerow(head)
        while next_page:
            school_feedbacks_url_list, next_page = collect_school_feedbacks_url(next_page)
            sleep(10)
            for url in school_feedbacks_url_list:
                data = fetch_feedback_data(url)
                writer.writerow(data.values())
                sleep(15)
    # for feedback in all_feedbacks:
    #     send_parse_data(fetch_feedback_data(feedback))


def write_data(data):
    with open('feedbacks_data.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        for row in data:
            writer.writerow(row)


if __name__ == '__main__':
    run_feedbacks_parser()
