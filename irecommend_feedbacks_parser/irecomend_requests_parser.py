import csv
from pprint import pprint
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from base_func.http_requests import create_cloudflare_scrapper, fetch_html_with_cloudflare
from base_func.utils import convert_to_date
from settings.logger_settings import logger


name = 'geekbrains'


def is_next_page(current_page_number: BeautifulSoup) -> bool:
    """ Определяет наличие следующей страницы с отзывами о курсе"""
    pagination = current_page_number.select_one('.pager')
    if not pagination:
        return False
    elif pagination.select_one('.pager-current') and pagination.select_one('.pager-last'):
        return True
    else:
        return False


def collect_school_feedbacks_url(url: str) -> List[str]:
    """ Парсинг ссылок на страницы с отзывами о школе

    Args:
        url (str): ссылка на первую страницу с отзывами о школе

    Returns:
        List[str]: список ссылок на полный текст отзывов о школе
    """
    next_page = True
    all_feedback_urls = list()
    current_page_number = 0
    while next_page:
        if current_page_number == 0:
            current_page = url + '?new=1'
        else:
            current_page = url + f'?page={current_page_number}&new=1'
        # all_feedbaks_on_page = fetch_html(current_page)
        # with open(f'all_feedbaks_on_page_{current_page_number}.html', 'w', encoding='utf-8') as file:
        #     file.write(all_feedbaks_on_page.text)
        with open(f'all_feedbaks_on_page_{current_page_number}.html', 'r', encoding='utf-8') as file:
            all_feedbaks_on_page = file.read()
        all_feedbaks_on_page = BeautifulSoup(all_feedbaks_on_page, 'lxml')
        urls_elements = all_feedbaks_on_page.select('.view .item-list .reviewTitle a')
        all_feedback_urls += ['https://www.irecommend.ru' + item['href'] for item in urls_elements]
        if is_next_page(all_feedbaks_on_page):
            current_page_number += 1
        else:
            break
    return all_feedback_urls


def find_text(text_bloks):
    return [item.get_text() for item in text_bloks if item]


def fetch_feedback_data(scraper, url: str, school_name: str) -> Optional[Dict]:
    """ Собирает данные со страницы с отзывом

    Args:
        url (str): ссылка на страницу с отзывом
        school_name (str): название школы о которой собираются отзывы

    Returns:
        Dict: собранные данные
    """
    feedbak_page = fetch_html_with_cloudflare(scraper, url)
    if feedbak_page:
        feedbak_page_soup = BeautifulSoup(feedbak_page.text, 'lxml')
        feedback_plus = find_text(feedbak_page_soup.select('.reviewBlock .plus li'))
        feedback_minus = find_text(feedbak_page_soup.select('.reviewBlock .minus li'))
        feedback_description = feedbak_page_soup.select_one('.reviewBlock .description p')
        feedback_date = feedbak_page_soup.select_one('.reviewBlock .dtreviewed [itemprop="datePublished"]')['content']
        rating: int = len(feedbak_page_soup.select('.reviewBlock .starsRating .star .on'))
        feedback_data = {
            'school': school_name,
            'feedback_source': 'https://www.irecommend.ru',
            'feedback_url': url,
            'feedback_plus': '; '.join(feedback_plus) if feedback_plus else None,
            'feedback_minus': '; '.join(feedback_minus) if feedback_minus else None,
            'feedback_description': feedback_description.get_text() if feedback_description else None,
            'feedback_date': str(convert_to_date(feedback_date)),
            'rating': rating,
        }
        return feedback_data
    else:
        logger.error(f'Страница с отзывом {feedbak_page} не доступна')
        return None



def test_irecomend(school_name: str) -> Optional[str]:
    # url = 'https://irecommend.ru/srch?query=geekbrains'
    # data = fetch_html(url)

    # with open('main_page.html', 'w', encoding='utf-8') as file:
    #     file.write(data.text)
    scraper = create_cloudflare_scrapper()
    with open('main_page.html', 'r', encoding='utf-8') as file:
        main_page = file.read()
    home_page_soup_data = BeautifulSoup(main_page, 'lxml')
    search_result = home_page_soup_data.select('.srch-result-nodes')

    for element in search_result:
        name = element.select_one('.title a').get_text()
        if school_name.lower() in name.lower():
            url = 'https://www.irecommend.ru' + element.select_one('.title a')['href']
            all_feedback_urls = collect_school_feedbacks_url(url)
            for url in all_feedback_urls:
                while True:
                    data = fetch_feedback_data(scraper, url, school_name)
                    if data:
                        with open('irecimend_data.csv', 'a', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow(data.values())
                        break
                    else:
                        scraper = create_cloudflare_scrapper()
                    
                
            # return url
    # logger.info(f'На сайте отстутствуют отзывы о школе {school_name}')
    # return None
