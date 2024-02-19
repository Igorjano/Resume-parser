import json
from configparser import ConfigParser


def get_token():
    """Function for gettind API token for telegram bot"""

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


def sorting(data):
    """This function sort candidates by skills match or completeness of the resume"""

    if [d for d in data if 'skills_match' in d.keys()]:
        res = sorted(data, key=lambda d: (d['match'], d['cv_fullness'], d['skills_num']), reverse=True)
    else:
        res = sorted(data, key=lambda d: (d['cv_fullness'], d['skills_num']), reverse=True)
    return res
