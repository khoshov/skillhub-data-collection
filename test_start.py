from otzovik_feedbacks_parser.otzovik_selenium_parse import run_feedbacks_parser
from government_support_courses.parser_support_courses import parse_supported_courses


if __name__ == "__main__":
    url = 'https://store.tildacdn.com/api/getproductslist/?storepartuid=765404065141&recid=339906850&c=1636115919658&getparts=true&getoptions=true&slice=1&size=100'
    # url = 'https://xn--b1agajda1bcigeoa6ahw4g.xn--p1ai/tproduct/1-843541215061-analitik-reklamnih-kampanii'
    parse_supported_courses(url)
