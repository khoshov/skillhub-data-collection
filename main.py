from settings.urls_config import TUTORTOP_MAIN_PAGE
from tutortop_parser.tutortop_parser import load_courses_data_by_category_url, load_main_page_course_links, write_data

if __name__ == '__main__':
    courses_category_links = load_main_page_course_links(TUTORTOP_MAIN_PAGE)
    for category, url in courses_category_links.items():
        data = load_courses_data_by_category_url(url, category)
        write_data(data)
