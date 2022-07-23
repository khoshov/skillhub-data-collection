

from otzovik_feedbacks_parser.otzovik_selenium_parse import run_otzovic_manual_parser
from old_code.otzovik_parser import run_feedbacks_parser
from tasks import run_tutortop_parser

# from irecommend_feedbacks_parser.irecomend_requests_parser import test_irecomend

from base_func.rucaptcha_api import solve_normal_captcha_api

if __name__ == '__main__':

    # url = 'http://otzovik.com/scripts/captcha/index.php?rand=5608674'
    # r = requests.get(url)
    # captcha_path = 'captcha.jpeg'
    # c = solve_normal_captcha(captcha_path)
    # print(c)
    
    # run_feedbacks_parser()
    
    # name = 'geekbrains'
    # test_irecomend(name)

    parsers = {
        1: run_tutortop_parser,
        2: run_otzovic_manual_parser
    }
    while True:
        parser_type = input(
            'Choose crawler: \n'
            '1 - Tutortop parser\n'
            '2 - Otzovic.ru parser\n'
            ''
        )
        if not parser_type.isdigit():
            print('Index must be the digit')
            continue
        parser_type = int(parser_type)
        if parser_type not in (1, 2):
            print('You choose the incorrect parser type. Try again.')
            continue
        break
    # run parser
    parsers.get(parser_type)()
