import requests
import requests_random_user_agent  # автоматически подставляет случайный user-agents, нужен только импорт

from settings.logger_settings import logger


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
