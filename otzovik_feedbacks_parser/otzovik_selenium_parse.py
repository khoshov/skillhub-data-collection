import os
from pprint import pprint
from time import sleep
from typing import List, Dict, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException

from base_func.http_requests import send_feedbacks_data, fetch_html
from base_func.web_session import start_browser
from base_func.utils import convert_to_date
from settings.logger_settings import logger


BAD_SCHOOL_NAMES = ('Курсы с Youtube', 'test')


def get_schools_list() -> Optional[Dict]:
    """ Получаем список школ и дату последенго отзыва, записанного в базе """
    response = fetch_html(os.getenv('SKILLHUB_GET_SCHOOLS')).json()
    if response:
        return response.get('results')
    return None


def find_school_feedbacks_url(browser, url: str):
    """ Получаем данные поискового get-запроса на главную страницу отзовик.ру """
    browser.get(url)
    try:
        warning_message = browser.find_element_by_css_selector('h1').text
        if warning_message == "Вы робот?":
            logger.error('https://otzovik.com/ заблокировал соединение. Требуется смена proxy')
            sleep(60)
    except NoSuchElementException:
        pass
    search_result = browser.find_elements_by_css_selector('.item.sortable')
    for element in search_result:
        if element.get_attribute('data-reviews') != '0':
            url = element.find_element_by_css_selector('a.product-name').get_attribute('href')
            url = url + '?order=date_desc'  # добавляем сортировку по дате
            return url


def collect_school_feedbacks_url(browser, url) -> List:
    """ Парсинг ссылок на отзывы о школе и ссылки на следующую страницу с отзывами """
    browser.get(url)
    feedbacks_urls = browser.find_elements_by_css_selector(".item-right h3 .review-title")
    school_feedbacks_url_list = [
        item.get_attribute('href') for item in feedbacks_urls
    ]
    # ищем на странице ссылку на следующую страницу, если ее нет, то это последняя страница
    try:
        next_page = browser.find_element_by_css_selector('a.next').get_attribute('href')
    except NoSuchElementException:
        next_page = None
    return school_feedbacks_url_list, next_page


def fetch_feedback_data(browser, url: str, school_name: str) -> Dict:
    """ Сбор и обработка данных отзыва """
    browser.get(url)
    feedback_plus = browser.find_element_by_css_selector(".review-plus").text
    feedback_minus = browser.find_element_by_css_selector(".review-minus").text
    feedback_description = browser.find_element_by_css_selector(".review-body.description").text
    feedback_description = feedback_description.replace('\n', ' ')
    feedback_date = browser.find_element_by_css_selector(".review-postdate .tooltip-right").text
    rating: int = len(browser.find_elements_by_css_selector("div.product-rating.tooltip-right .icons.icon-star-1"))
    feedback_data = {
        'school': school_name,
        'feedback_source': 'https://otzovik.com/',
        'feedback_url': url,
        'feedback_plus': feedback_plus,
        'feedback_minus': feedback_minus,
        'feedback_description': feedback_description,
        'feedback_date': str(convert_to_date(feedback_date)),
        'rating': rating,
    }
    return feedback_data


def parse_school_feedbacks(school: Dict, parse_all_feedbacks: bool = False):
    """ Парсинг отзывов о школе и направление обработанных данных API SkillHub """
    school_name = school.get('name')
    logger.info(f'Начат сбор отзывов с otzovik.com о школе {school_name}')
    try:
        browser = start_browser()
        search_url = f"https://otzovik.com/?search_text={school_name}&x=8&y=10"
        sleep(10)
        next_page = find_school_feedbacks_url(browser, search_url)
        while next_page:
            school_feedbacks_url_list, next_page = collect_school_feedbacks_url(browser, next_page)
            sleep(10)
            for url in school_feedbacks_url_list:
                if not parse_all_feedbacks and url == school.get('latest_review_url'):
                    next_page = ''
                    break
                try:
                    data = fetch_feedback_data(browser, url, school_name)
                    send_feedbacks_data(data)
                except TimeoutException as e:
                    logger.warning(f"{e}. Медленная скорость работы через прокси сервер")
                finally:
                    sleep(15)
    except TimeoutException as e:
        logger.warning(f"{e}. Медленная скорость работы через прокси сервер")
    except NoSuchElementException as e:
        logger.error(f"Во время парсинга произошла ошибка {e}")
    finally:
        browser.close()
        browser.quit()
        logger.info(f'Завершен сбор отзывов с otzovik.com о школе {school_name}')


def run_feedbacks_parser(schools_data: List[Dict], school_name: Optional[str] = None):
    """ Choose mode and run crawler """
    while True:
        crawler_mode = input(
            'Choose crawler mode: \n'
            '0 - parse only latest feedbacks\n'
            '1 - parse all feedbacks\n'
            ''
        )
        if not crawler_mode.isdigit():
            print('Index must be the digit')
            continue
        crawler_mode = int(crawler_mode)
        if crawler_mode not in (0, 1):
            print('You choose the incorrect crawler mode. Try again.')
            continue
        break
    if school_name:
        logger.info(f'Парсер отзывов о школе {school_name} с otzovik.com начал работу')
        school = next((item for item in schools_data if item["name"] == school_name), None)
        parse_school_feedbacks(school, parse_all_feedbacks=bool(crawler_mode))
    else:
        logger.info('Парсер всех отзывов с otzovik.com начал работу')
        for school in schools_data:
            if school.get("name") not in BAD_SCHOOL_NAMES:
                parse_school_feedbacks(school, parse_all_feedbacks=bool(crawler_mode))
    logger.info('Парсер отзывов с otzovik.com закончил работу')


def run_otzovic_manual_parser():
    """ Starting data crawling process """
    schools_data = get_schools_list()
    if not schools_data:
        logger.error('Не удалось получить список школ из API SkillHub. Парсер отзывов не был запущен')
        return

    school_names_in_db = {number: school.get("name") for number, school in enumerate(schools_data, start=1) if (
        school.get("name") not in BAD_SCHOOL_NAMES)}
    while True:
        pprint(school_names_in_db)
        school_name_index = input("Please enter school index or enter 0 to crawl data about all schools: ")
        if not school_name_index.isdigit():
            print('Index must be the digit')
            continue
        school_name_index = int(school_name_index)
        if school_name_index != 0 and school_name_index not in list(school_names_in_db.keys()):
            print("You choose unexpected index. Please try again")
            continue
        break

    if school_name_index == 0:
        run_feedbacks_parser(schools_data)
    run_feedbacks_parser(schools_data, school_names_in_db.get(school_name_index))
