import json
from configparser import ConfigParser


def get_token():
    """Function for getting API token for telegram bot"""

    config = ConfigParser()
    config.read('secrets')
    telegram_section = config['telegram']
    token = telegram_section['token']
    return token


def load_data():
    """Read file with info of candidates after parsing pages with RobotaUaParser or WorkUaParser"""

    try:
        with open('candidates.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return data
    except NameError:
        print('File not found!')


def sorting_data(data):
    """This function sort candidates by skills match or completeness of the resume"""

    if any('skills_match' in d for d in data):
        res = sorted(data, key=lambda d: (d['skills_match'], d['cv_fullness'], d['skills_num']), reverse=True)
    else:
        res = sorted(data, key=lambda d: (d['cv_fullness'], d['skills_num']), reverse=True)
    return res
