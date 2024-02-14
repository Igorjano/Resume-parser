import json

from RabotaUa import RobotaUaParser
from WorkUa import WorkUaParser


def main():
    print('''What site do you want to use for searching?
    1 - robota.ua
    2 - work.ua
    For exit enter 0\n''')
    # num = input('Enter the number:\t')

    # parser = source_choice(num)
    # parser.parse()
    candidates = load_data()
    print('Preparing the most relevant...')
    result = sorting(candidates)
    print_candidates(result[:6])


def load_data():
    try:
        with open('candidates_work_ua.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return data
    except NameError:
        print('File not found!')


def source_choice(number):
    while number not in ['0', '1', '2']:
        number = input('You enter wrong number! Please try again:\t')
    if number == '1':
        return RobotaUaParser()
    elif number == '2':
        return WorkUaParser()
    elif number == '0':
        exit()


def sorting(data):
    if [d for d in data if 'skills_match' in d.keys()]:
        res = sorted(data, key=lambda d: (d['match'], d['skills_num'], d['cv_fullness']), reverse=True)
    else:
        res = sorted(data, key=lambda d: (d['cv_fullness'], d['skills_num']), reverse=True)
    return res


def print_candidates(candidates):
    for candidate in candidates:
        print(f"{candidate['position']}   {candidate['name']}    {candidate['cv_page']}")
        print('='*100)


if __name__ == '__main__':
    main()
