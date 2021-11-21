"""file contains mapping functions"""

COURSE_CATEGORY_ALIAS = {
    'QA-тестирование': ['qa', 'тестирование', ' тестировщик'],
    'Python-разработка': ['python', 'питон'],
    'Web-разработка': ['web'],
    'JavaScript': ['javascript'],
    'Fullstack-разработчик': ['fullstack'],
    'Java-разработка': ['java'],
    'Frontend-разработка': ['frontend'],
    'PHP-разработка': ['php'],
    'Разработка игр на Unity': ['unity'],
    'Разработка на C#': ['c#'],
    'DevOps': ['devops'],
    'IOS и Android': ['ios и android'],
    'Android-разработка': ['android'],
    'IOS-разработка': ['ios'],
    'Верстка на HTML/CSS': ['html', 'css'],
    'Разработка на C++': ['c++'],
    'Разработка игр на Unreal Engine': ['unreal engine'],
    'Разработка на Kotlin': ['kotlin'],
    'Разработка на Swift': ['swift'],
    'Golang-разработка': ['golang'],
    '1C-разработка': ['1с', '1c'],
    'VR/AR разработка': ['vr/ar'],
    'Data scienсe': ['data scienсe'],
    'Big Data': ['big data']
}


def gouverment_couts_category_mapping(course_name: str) -> str:
    """Find course category by key words in course name"""
    for category_name, items in COURSE_CATEGORY_ALIAS.items():
        if any(item in course_name.lower() for item in items):
            return category_name
    return 'Цифровые профессии'
