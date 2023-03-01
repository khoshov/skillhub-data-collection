
from otzovik_feedbacks_parser.otzovik_selenium_parser import run_itzovik_manual_parser
from irecommend_feedbacks_parser.irecommend_selenium_parser import run_irecommend_manual_parser
from mooc_feedbacks_parser.mooc_requests_parser import run_mooc_parser
from sravnyator_feedback_parser.sravnyator_requests_parser import run_sravnytor_parser
from yell_feedbacks_parser.yell_requests_parser import run_yell_parser
from two_gis_feedbacks_parser.two_gis_requests_parser import run_2gis_parser


if __name__ == '__main__':
    parsers = {
        1: run_itzovik_manual_parser,
        2: run_irecommend_manual_parser,
        3: run_mooc_parser,
        4: run_yell_parser,
        5: run_sravnytor_parser,
        6: run_2gis_parser
    }
    while True:
        parser_type = input(
            'Choose crawler: \n'
            '1 - otzovik.ru parser\n'
            '2 - irecommend.ru parser\n'
            '3 - mooc.ru parser\n'
            '4 - yell.ru parser\n'
            '5 - journal.tinkoff.ru/sravnyator parser\n'
            '6 - 2gis.ru parser\n'
        )
        if not parser_type.isdigit():
            print('Index must be the digit')
            continue
        parser_type = int(parser_type)
        if parser_type not in parsers.keys():
            print('You choose the incorrect parser type. Try again.')
            continue
        break
    # run parser
    parsers.get(parser_type)()
