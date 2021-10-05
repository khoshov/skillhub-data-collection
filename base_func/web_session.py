import os

from dotenv import load_dotenv
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver


load_dotenv()


def start_browser():
    """инициальзирует Selenium browser"""
    proxy = os.getenv("PROXIES")
    ua = UserAgent(verify_ssl=False)
    options = Options()

    # новые настройки selenium
    options.headless = True  # фоновый режим
    options.add_argument("start-maximized")
    options.page_load_strategy = 'eager'  # ожидание основной загрузки страницы
    options.add_argument(f'user-agent={ua.firefox}')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disk-cache-size=1000")
    options.add_argument("--media-cache-size=1000")
    options.add_argument("window-size=1920,1080")

    # # старые настройки selenium
    # options.add_argument(f'user-agent={ua.firefox}')
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--disable-gpu")
    # options.add_argument('--headless')  # фоновый режим
    # options.page_load_strategy = 'eager'  # ожидание основной загрузки страницы
    # options.add_argument("--disable-extensions")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-application-cache")
    # options.add_argument("--disk-cache-size=1000")
    # options.add_argument("--media-cache-size=1000")
    # options.add_argument("--window-size=1920x1080")

    proxy_options = {
        'proxy': {
            'http': proxy,
            'https': proxy,
        }
    }

    browser = webdriver.Chrome(
        '/home/skillhub_parsers/chromedriver',
        seleniumwire_options=proxy_options,
        options=options
    )

    # browser = webdriver.Chrome(
    #     '/Users/gump85/Documents/python_work/chromedriver',
    #     # seleniumwire_options=proxy_options,
    #     options=options
    # )

    browser.implicitly_wait(5)
    browser.set_page_load_timeout(120)

    return browser
