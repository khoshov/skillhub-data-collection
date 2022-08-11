from distutils.util import strtobool
import os

from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc

from settings.browser_config import USER_AGENT


load_dotenv()

CHROME_ARGUMENTS = [
    '--start-maximized', f'--user-agent={USER_AGENT}',
    '--no-first-run', '--no-service-autorun', '--password-store=basic',
    '--disable-blink-features=AutomationControlled', '--disable-extensions',
    '--disable-dev-shm-usage', '--disable-application-cache', '--disk-cache-size=1000',
    '--media-cache-size=1000',
    '--disable-background-networking', '--disable-bundled-ppapi-flash',
    '--disable-client-side-phishing-detection',
    '--disable-component-extensions-with-background-pages',
    '--disable-component-update', '--disable-default-apps',
    '--disable-device-discovery-notifications',
    '--disable-gpu', '--disable-notifications',
    '--disable-search-geolocation-disclosure', '--disable-sync',
    '--ignore-certificate-errors', '--no-default-browser-check',
]


def start_browser():
    """инициальзирует Selenium browser"""
    # proxy = os.getenv("PROXIES")
    options = Options()
    for argument in CHROME_ARGUMENTS:
        options.add_argument(argument)
    # запуск в фоновом режиме
    if strtobool(os.getenv('HEADLESS_MODE')):
        options.headless = True
        options.add_argument('--no-sandbox')
    options.page_load_strategy = 'eager'  # ожидание основной загрузки страницы

    service = Service(executable_path=os.getenv('WEBDRIVER_PATH'))

    browser = uc.Chrome(
        service=service,
        options=options
    )

    browser.implicitly_wait(5)
    browser.set_page_load_timeout(120)
    return browser
