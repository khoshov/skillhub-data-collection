

from otzovik_feedbacks_parser.otzovik_selenium_parser import run_itzovik_manual_parser
from irecommend_feedbacks_parser.irecommend_selenium_parser import run_irecommend_manual_parser


if __name__ == '__main__':
    parsers = {
        1: run_itzovik_manual_parser,
        2: run_irecommend_manual_parser
    }
    while True:
        parser_type = input(
            'Choose crawler: \n'
            '1 - otzovik.ru parser\n'
            '2 - irecommend.ru parser\n'
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
