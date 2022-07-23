import os

from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException, NetworkException

from dotenv import load_dotenv

from settings.logger_settings import logger


load_dotenv()

rucaptcha_api_key = os.getenv("RUCAPTCHA_API_KEY")
solver = TwoCaptcha(rucaptcha_api_key)


def solve_normal_captcha_api(path_to_captcha: str) -> str:
    """
    Решает обычную простую капчу через API https://rucaptcha.com/
    """
    try:
        result = solver.normal(path_to_captcha)
        logger.info(f'Капча решена code = {result.get("code")}')
        return result.get('code')
    except (NetworkException, ApiException) as error:
        logger.warning(f'Не удалось распознать капчу {error}')
        return None
