import csv
import re
import os
from pprint import pprint
from time import sleep
from typing import List, Dict, Optional, Tuple

from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

from base_func.http_requests import send_feedbacks_data, fetch_html
from base_func.rucaptcha_api import solve_normal_captcha_api
from base_func.web_session import start_browser
from base_func.date_tools import convert_to_date
from settings.logger_settings import logger


BAD_SCHOOL_NAMES = ('Курсы с Youtube', 'test')


def run_irecommend_update_data_job():
    """ Задача для автоматического обновления последних отзывов во всех школах """
    schools_data = get_schools_list()
    browser = start_browser()
    logger.info('Парсер обновления отзывов с irecommend.com начал работу')
    for school in schools_data:
        if school.get("name") not in BAD_SCHOOL_NAMES:
            parse_school_feedbacks(browser, school)
    browser.close()
    browser.quit()
    logger.info('Парсер закончил обновлять отзывы с irecommend.com')


def get_schools_list() -> Optional[Dict]:
    """ Получаем список школ и дату последенго отзыва, записанного в базе """
    response = fetch_html(os.getenv('SKILLHUB_GET_SCHOOLS')).json()
    if response:
        return response.get('results')
    return None


def find_school_feedbacks_url(browser, school_name: str) -> Optional[str]:
    """ Получаем данные поискового get-запроса на главную страницу отзовик.ру """
    search_url = f"https://irecommend.ru/srch?query={school_name}"
    browser = open_url(browser, search_url)

    try:
        search_result = browser.find_element_by_css_selector('.srch-result-nodes .title a')
        # проверяем вхождения названия школы в поисковый результат
        if school_name.lower() in search_result.text.lower():
            url = search_result.get_attribute('href')
            url = url + '?page=0&new=1'  # номер страницы добавляем сортировку по дате
            return url
    except NoSuchElementException:
        pass
    logger.info(f'На сайте отстутствуют отзывы о школе {school_name}')
    return None


def collect_school_feedbacks_url(browser, url: str) -> Tuple:
    """ Парсинг ссылок на отзывы о школе и ссылки на следующую страницу с отзывами """
    browser = open_url(browser, url)
    feedbacks_urls = browser.find_elements_by_css_selector(".list-comments .item .reviewTitle a")
    school_feedbacks_url_list = [
        item.get_attribute('href') for item in feedbacks_urls
    ]
    # ищем на странице ссылку на следующую страницу, если ее нет, то это последняя страница
    try:
        pagination = browser.find_element(By.CSS_SELECTOR, '.pager')
        page_current = pagination.find_element(By.CSS_SELECTOR, '.pager-current').text
        # проверяем наличие ссылки на последюнюю страницу, если ее нет, то станица текущая страница - последняя
        page_last = pagination.find_element(By.CSS_SELECTOR, '.pager-last')
        # на сайте нумерация страниц в url идет с нуля
        next_page = re.sub(r"page=\d{1,2}", rf"page={page_current}", url)
    except NoSuchElementException:
        next_page = None
    return school_feedbacks_url_list, next_page


def fetch_feedback_data(browser, url: str, school_name: str) -> Dict:
    """ Сбор и обработка данных отзыва """
    browser = open_url(browser, url)
    try:
        feedback_plus = browser.find_element(By.CSS_SELECTOR, '.reviewBlock .ratio .plus ul').text
        feedback_plus = feedback_plus.replace('\n', ' ')
    except NoSuchElementException:
        feedback_plus = None
    try:
        feedback_minus = browser.find_element(By.CSS_SELECTOR, '.reviewBlock .ratio .minus ul').text
        feedback_minus = feedback_minus.replace('\n', ' ')
    except NoSuchElementException:
        feedback_minus = None
    feedback_description = browser.find_element(By.CSS_SELECTOR, '.reviewBlock .reviewText').text
    feedback_description = feedback_description.replace('\n', ' ')
    feedback_date = browser.find_element(By.CSS_SELECTOR, '.reviewBlock .dtreviewed meta').get_attribute('content')
    feedback_date = feedback_date.split('T')[0]  # удаляем время из данных
    rating: int = len(browser.find_elements_by_css_selector(".reviewBlock .fivestarWidgetStatic .on"))
    feedback_data = {
        'school': school_name,
        'feedback_source': 'https://irecommend.ru/',
        'feedback_url': url,
        'feedback_plus': feedback_plus,
        'feedback_minus': feedback_minus,
        'feedback_description': feedback_description,
        'feedback_date': str(convert_to_date(feedback_date)),
        'rating': rating,
    }
    return feedback_data


def parse_school_feedbacks(browser, school: Dict, parse_all_feedbacks: bool = False):
    """ Парсинг отзывов о школе и направление обработанных данных API SkillHub """
    school_name = school.get('name')
    logger.info(f'Старт сбора отзывов с irecommend.com о школе {school_name}')
    try:
        sleep(5)
        next_page = find_school_feedbacks_url(browser, school_name)
        if not next_page:
            logger.info(f'На http://irecomend.ru отсутствуют отзывы о шкоел {school_name}')
            return

        while next_page:
            school_feedbacks_url_list, next_page = collect_school_feedbacks_url(browser, next_page)
            sleep(5)
            for url in school_feedbacks_url_list:
                if not parse_all_feedbacks and url == school.get('latest_review_url'):
                    next_page = ''
                    break
                try:
                    data = fetch_feedback_data(browser, url, school_name)
                    send_feedbacks_data(data)
                    # with open('irecimend_data.csv', 'a', encoding='utf-8') as f:
                    #     writer = csv.writer(f, delimiter='|')
                    #     writer.writerow(data.values())
                except TimeoutException as e:
                    logger.warning(f"{e}. Медленная скорость работы сети")
                finally:
                    sleep(5)
        logger.info(f'Завершен сбор отзывов с irecomend.ru о школе {school_name}')
    except TimeoutException as e:
        logger.warning(f"{e}. Медленная скорость работы сети")
    except NoSuchElementException as e:
        browser.save_screenshot('error.png')
        with open('page.html', 'w+') as f:
            f.write(browser.page_source)
        logger.error(f"Во время парсинга произошла ошибка {e}")


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

    browser = start_browser()
    try:
        if school_name:
            logger.info(f'Парсер отзывов о школе {school_name} с irecomend.ru начал работу')
            school = next((item for item in schools_data if item["name"] == school_name), None)
            parse_school_feedbacks(browser, school, parse_all_feedbacks=bool(crawler_mode))
        else:
            logger.info('Парсер всех отзывов с irecomend.ru начал работу')
            for school in schools_data:
                if school.get("name") not in BAD_SCHOOL_NAMES:
                    parse_school_feedbacks(browser, school, parse_all_feedbacks=bool(crawler_mode))
    finally:
        browser.close()
        browser.quit()
    logger.info('Парсер отзывов с irecomend.ru закончил работу')


def run_irecommend_manual_parser():
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
    else:
        run_feedbacks_parser(schools_data, school_names_in_db.get(school_name_index))


def open_url(browser: uc.Chrome, url: str):
    """ Открывает страницу по ссылке, если соединение блокируется - решает капчу """
    browser.get(url)
    sleep(3)
    try:
        warning_message = browser.find_element(By.CSS_SELECTOR, 'h1').text
        if warning_message == "Вы робот?":
            solve_captcha(browser)
            # если капча распознана верно браузер будет перенаправлен на главную страницу
            # повторим попытку поиска
            sleep(2)
            browser.get(url)
            sleep(3)
    except NoSuchElementException:
        pass
    except WebDriverException as e:
        logger.warning(f'Во время работы вебдрайвера возникла ошибка: {e}')
        browser.close()
        browser.quit()
        browser = start_browser()
        open_url(browser, url)
    return browser


def solve_captcha(browser):
    """
    Решает капчу на странице блокировки
    """
    logger.warning('https://irecomend.ru/ заблокировал соединение. Решаем капчу')
    captcha_image_element = browser.find_element(By.CSS_SELECTOR, 'img')
    captcha_input_field = browser.find_element(By.CSS_SELECTOR, 'td input[type="text"]')
    submit_button = browser.find_element(By.CSS_SELECTOR, 'td input[type="submit"')
    captcha_path = 'captcha.png'
    captcha_image_element.screenshot(captcha_path)
    while True:
        captcha = solve_normal_captcha_api(captcha_path)
        if captcha:
            break
    captcha_input_field.send_keys(captcha)
    sleep(3)
    submit_button.click()
