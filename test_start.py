from otzovik_feedbacks_parser.otzovik_selenium_parse import run_feedbacks_parser
from government_support_courses.parser_support_courses import parse_supported_courses
from settings.urls_config import TUTORTOP_MAIN_PAGE
from tutortop_parser.tutortop_parser import load_courses_data_by_category_url, load_main_page_course_links


if __name__ == "__main__":
    # url = 'https://store.tildacdn.com/api/getproductslist/?storepartuid=765404065141&recid=339906850&c=1636115919658&getparts=true&getoptions=true&slice=1&size=100'
    # url = 'https://xn--b1agajda1bcigeoa6ahw4g.xn--p1ai/tproduct/1-843541215061-analitik-reklamnih-kampanii'
    # parse_supported_courses(url)
    courses_category_links = load_main_page_course_links(TUTORTOP_MAIN_PAGE)
    for category, url in courses_category_links.items():
        load_courses_data_by_category_url(url, category)
