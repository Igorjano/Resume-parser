"""
This script performs candidate searching on job websites (robota.ua or work.ua)
and outputs five the most relevant candidates based on specified criteria.
"""

from typing import Union, Tuple, Optional, List, Dict

from utils import load_data, sorting_data
from parsers.RobotaUa import RobotaUaParser
from parsers.WorkUa import WorkUaParser


def main() -> None:
    """
    Main function to execute the candidate search and display the most relevant results.
    """

    print('1 - robota.ua\n2 - work.ua\nFor exit enter 0\n')
    num = input('What site do you want to use for searching?\t')

    p = source_choice(num)
    p.parse()
    candidates = load_data()
    print('Preparing the most relevant...')
    result = sorting_data(candidates)
    print_candidates(result[:5])


def source_choice(number: str) -> Union[RobotaUaParser, WorkUaParser, None]:
    """
    Selects the parser based on the user's input.

    Parameters:
    - number (str): The user's input for selecting the source.

    Returns:
    Union[RobotaUaParser, WorkUaParser, None]: An instance of RobotaUaParser or WorkUaParser based on user's choice,
    or None if the user chooses to exit.
    """

    category, search_text, location, years_of_exp, salary_min, salary_max, photos = select_options()

    while number not in ['0', '1', '2']:
        number = input('You enter wrong number! Please try again:\t')
    if number == '1':
        return RobotaUaParser(category, search_text, location, years_of_exp, salary_min, salary_max, photos)
    elif number == '2':
        return WorkUaParser(category, search_text, location, years_of_exp, salary_min, salary_max, photos)
    elif number == '0':
        exit()


def select_options() -> Tuple[str, str, Optional[str], Optional[int],
                              Optional[int], Optional[int], Optional[bool]]:
    """
    Selects search options from the user.

    Returns:
    Tuple[str, str, Optional[str], Optional[int], Optional[int], Optional[int], Optional[bool]]: A tuple containing
    search options - category, search_text, location, years_of_exp, salary_min, salary_max, photos.
    """

    category = select_category()
    search_text = input('What are we looking for?\t')

    print('Please enter additional search parameters. If you want to leave fields empty just press Enter')

    location = input('Location:\t')
    location = location if location != '' else None

    years_of_exp = input('If you want only candidates without experience enter 0. Years of experience:\t')
    years_of_exp = validate(years_of_exp) if years_of_exp != '' else None

    salary_min = input('Enter min salary expected:\t')
    salary_min = validate(salary_min) if salary_min != '' else None

    salary_max = input('Enter max salary expected:\t')
    salary_max = validate(salary_max) if salary_max != '' else None

    photos = input('Enter yes/no to show resumes with photo only:\t')
    photos = True if photos == 'yes' else None

    return category, search_text, location, years_of_exp, salary_min, salary_max, photos


def select_category() -> str:
    """
    Selects the search category from the user.

    Returns:
    str: The selected category (either '1' or '2').
    """

    category = input('Choose category in what you want to search:\n1 - Job position\n2 - Skills or keywords\t')
    while category != '1' and category != '2':
        category = input('There are no such category! Please try again:\t')
    return category


def validate(value: Union[str, int]) -> int:
    """
    Validates and converts the input value to an integer.

    Parameters:
    - value (Union[str, int]): The input value to be validated.

    Returns:
    int: The validated integer value.
    """

    while not type(value) is int:
        try:
            value = int(value)
        except ValueError:
            value = input('Enter integer number:\t')
    return value


def print_candidates(candidates: List[Dict[str, Union[str, int]]]) -> None:
    """
    Print sorted and most relevant candidates.

    Parameters:
    - candidates (List[Dict[str, Union[str, int]]]): A list of candidate dictionaries.
    """

    for candidate in candidates:
        print(f"{candidate['position']}   {candidate['name']}    {candidate['cv_page']}")
        print('='*100)


if __name__ == '__main__':
    main()
