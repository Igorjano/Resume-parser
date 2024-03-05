from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import List, Dict, Optional, Union
import json


class RobotaUaParser:
    """
    RobotaUaParser is a class for parsing candidate information from Robota.ua website.

    Attributes:
    - url (str): The URL of the Robota.ua candidates page.
    - result (list): A list to store all parsed candidates information.
    - keywords (list): A list of keywords to match with candidate skills.
    - candidate_info (dict): A dictionary to store individual candidate information.
    - keywords (list): A list of keywords to match with candidate skills.
    - location (str): Name of the city to filter candidates.
    - years_of_exp (int): The minimum years of experience required for candidates.
    - salary_min (int): The minimum salary expected for candidates.
    - salary_max (int): The maximum salary expected for candidates.
    - photo (bool): Flag to include candidate photos in the results.
    - options (webdriver.ChromeOptions): ChromeOptions for configuring the Chrome WebDriver.
    - driver (webdriver.Chrome): The Chrome WebDriver for interacting with the website.
    """

    def __init__(self, category: str,
                 text: str,
                 location: Optional[str],
                 experience: Optional[int],
                 salary_min: Optional[int],
                 salary_max: Optional[int],
                 photo: bool) -> None:
        """
        Initializes the RobotaUaParser object.

        Parameters:
        - category (str): The category of the search.
        - text (str): The search text for job position or keywords.
        - location (Optional[str]): Name of the city to filter candidates.
        - experience (Optional[int]): The minimum years of experience required for candidates.
        - salary_min (Optional[int]): The minimum salary expected for candidates.
        - salary_max (Optional[int]): The maximum salary expected for candidates.
        - photo (bool): Flag to include candidate photos in the results.
        """

        self.url = 'https://robota.ua/candidates/all'
        self.result: List[dict] = []
        self.keywords: Optional[List[str]] = None
        self.category: str = category
        self.search_text: str = text
        self.location: Optional[str] = location
        self.years_of_exp: Optional[int] = experience
        self.salary_min: Optional[int] = salary_min
        self.salary_max: Optional[int] = salary_max
        self.photo: bool = photo

        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--blink-settings=imagesEnabled=false")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(options=self.options)

    def parse(self) -> List[dict]:
        """
        Initiates the parsing process and returns the parsed candidate information.

        Returns:
        list: List of dictionaries containing all parsed candidates information.
        """

        self.driver.get(self.url)
        self.set_options()

        if self.get_number_of_cv() == '0':
            print('There are no candidates according to the given criteria')
            self.driver.quit()
            self.upload_to_json()
            return self.result

        # Check if we have pages navigation
        try:
            self.get_cv_links()
            pages = (self.driver.find_element(By.CLASS_NAME, 'paginator').
                     find_elements(By.TAG_NAME, 'a'))

            if len(pages) > 5:
                self.parse_next_btn()
            else:
                self.parse_pages(len(pages))

            self.driver.quit()
            self.upload_to_json()
            return self.result

        except NoSuchElementException:
            self.driver.quit()
            self.upload_to_json()
            return self.result

    def get_number_of_cv(self) -> str:
        """
        Gets the number of candidates available based on the given criteria.

        Returns:
        str: The number of candidates found.
        """

        number_elm = (WebDriverWait(self.driver, 20).
                      until(EC.presence_of_element_located((By.TAG_NAME,
                                                            'alliance-employer-cvdb-search-header'))))

        number = number_elm.find_element(By.CLASS_NAME, 'santa-text-red-500').text
        print(f'Was found {number} candidate(-tes)')
        return number

    def set_options(self) -> None:
        """Sets options for the parser."""

        print('Setting options ...')
        self.set_category()
        self.set_location()
        self.show_photo()
        self.set_experience()
        self.set_salary()
        print('Searching ...')
        sleep(1)

    def set_category(self) -> None:
        """Sets the category based on the provided input (job position or keywords)."""

        if self.category == '1':
            self.set_search_text(self.search_text)
        elif self.category == '2':
            self.keywords = self.search_text.split()
            self.switch_category()
            self.set_search_text(self.search_text)

    def switch_category(self) -> None:
        """Switches the category in the search mode."""

        category_list = (WebDriverWait(self.driver, 20).
                         until(EC.element_to_be_clickable((By.TAG_NAME,
                                                          'alliance-employer-cvdb-desktop-search-mode'))))
        category_list.click()
        try:
            category = (WebDriverWait(category_list, 20).
                        until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'p'))))

            category[4].click()
        except TimeoutException:
            print('Something wrong with the category')

    def set_search_text(self, text: str) -> None:
        """
        Sets the search text in the input field.

        Parameters:
        - text (str): The search text or keywords.
        """

        search_input_elm = (WebDriverWait(self.driver, 20).
                            until(EC.visibility_of_element_located((By.TAG_NAME, 'santa-suggest-input'))))

        search_input = search_input_elm.find_element(By.TAG_NAME, 'input')
        search_input.send_keys(text)
        search_input.send_keys(Keys.RETURN)
        sleep(1)

    def set_location(self) -> None:
        """Sets the name of the city to filter candidates."""

        if self.location:
            loc_search = (WebDriverWait(self.driver, 20).
                          until(EC.element_to_be_clickable((By.TAG_NAME,
                                                            'alliance-employer-cvdb-desktop-filter-city'))))

            loc_search.click()
            loc_search.find_element(By.TAG_NAME, 'input').send_keys(self.location)
            sleep(1)
            try:
                (WebDriverWait(loc_search, 20).
                 until(EC.element_to_be_clickable((By.TAG_NAME, 'li')))).click()

            except TimeoutException:
                print('You enter the wrong location! Location set to all Ukraine')

    def set_experience(self) -> None:
        """Sets the experience filter for candidates."""

        if self.years_of_exp:
            filters_elm = (WebDriverWait(self.driver, 20).
                           until(EC.presence_of_element_located((By.TAG_NAME,
                                                                 'alliance-employer-cvdb-simple-experience'))))

            list_elm = (WebDriverWait(filters_elm, 20).
                        until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'list-item'))))

            for checkbox in list_elm:
                # Get labels of checkboxes because it changes dynamically
                text_lbl = (WebDriverWait(checkbox, 20).
                            until(EC.presence_of_element_located((By.TAG_NAME, 'p'))))

                # Get the numbers from the string
                years = [y for y in text_lbl.text.split() if y.isdigit()]
                if not len(years):
                    if self.years_of_exp == 0:
                        checkbox.find_element(By.TAG_NAME, 'santa-checkbox').click()
                elif len(years) == 1:
                    if years[0] == '1':
                        if self.years_of_exp < 1:
                            checkbox.find_element(By.TAG_NAME, 'santa-checkbox').click()
                    elif years[0] == '10':
                        if self.years_of_exp >= 10:
                            checkbox.find_element(By.TAG_NAME, 'santa-checkbox').click()
                else:
                    if int(years[0]) <= self.years_of_exp < int(years[1]):
                        checkbox.find_element(By.TAG_NAME, 'santa-checkbox').click()

    def set_salary(self) -> None:
        """Sets the salary range filter for candidates."""

        range_elm = (WebDriverWait(self.driver, 20).
                     until(EC.presence_of_element_located((By.TAG_NAME, 'alliance-employer-cvdb-simple-salary'))))

        input_elm = range_elm.find_element(By.TAG_NAME, 'lib-input-range')
        min_input, max_input = input_elm.find_elements(By.TAG_NAME, 'input')

        if self.salary_min:
            min_input.send_keys(self.salary_min)
            min_input.send_keys(Keys.RETURN)

        if self.salary_max:
            max_input.send_keys(self.salary_max)
            max_input.send_keys(Keys.RETURN)

    def show_photo(self) -> None:
        """Toggles the visibility of candidate photos."""

        if self.photo:
            (WebDriverWait(self.driver, 20).
             until(EC.element_to_be_clickable((By.TAG_NAME, 'santa-toggler')))).click()

    # If we have more than 5 pages use next button for navigation
    def parse_next_btn(self) -> List[dict]:
        """
        Navigates through pages using the 'Next' button.

        Returns:
        list: List of dictionaries containing all parsed candidates information.
        """

        while True:
            try:
                next_btn = (WebDriverWait(self.driver, 10).
                            until(EC.presence_of_element_located((By.CLASS_NAME, 'next'))))

                next_btn.click()
                self.get_cv_links()

            except TimeoutException:
                self.driver.quit()
                return self.result

    # Click on every next page link
    def parse_pages(self, number: int) -> List[dict]:
        """
        Navigates through multiple pages.

        Parameters:
        - number (int): The number of pages to navigate.

        Returns:
        list: List of dictionaries containing all parsed candidates information.
        """

        for i in range(number - 1):
            pages_elm = (WebDriverWait(self.driver, 20).
                         until(EC.presence_of_element_located((By.CLASS_NAME, 'paginator'))))

            pages_links = (WebDriverWait(pages_elm, 20).
                           until(EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))))

            pages_links[i + 1].click()
            self.get_cv_links()

        self.driver.quit()
        return self.result

    def get_cv_links(self) -> None:
        """Gets the links to individual candidate profiles."""

        try:
            cv_elms = (WebDriverWait(self.driver, 20).
                       until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'cv-card'))))

            links = [WebDriverWait(elm, 10).
                     until(EC.visibility_of_element_located((By.TAG_NAME, 'a'))).
                     get_attribute("href") for elm in cv_elms]

            current_window_handle = self.driver.current_window_handle

            with ThreadPoolExecutor(max_workers=20) as executor:
                executor.map(self.open_cv_pages, links)

            handles = self.driver.window_handles
            for handle in handles:
                if handle != current_window_handle:
                    self.driver.switch_to.window(handle)
                    self.result.append(self.get_cv_data())
                    self.driver.close()

            self.driver.switch_to.window(current_window_handle)
            print(f'{len(self.result)} candidates was downloaded')

        except TimeoutException:
            print('Something went wrong! ')
            self.driver.quit()

    def open_cv_pages(self, page_link: str) -> None:
        """
        Opens individual candidate profile pages.

        Parameters:
        - page_link (str): The URL of the candidate's profile page.
        """

        self.driver.execute_script(f"window.open('{page_link}');")

    def get_cv_data(self) -> Dict:
        """
        Gets data from individual candidate profiles.

        Returns:
        dict: Dictionary containing candidate information.
        """

        candidate_info = {}

        position_elm = (WebDriverWait(self.driver, 20).
                        until(EC.presence_of_element_located((By.TAG_NAME, 'lib-resume-main-info'))))

        candidate_info['position'] = (position_elm.
                                      find_element(By.CLASS_NAME, 'santa-typo-secondary ')).text

        candidate_info['name'] = self.driver.find_element(By.CLASS_NAME, 'santa-typo-h2').text
        candidate_info['cv_page'] = self.driver.current_url
        candidate_info['cv_fullness'] = self.get_score()
        candidate_info['skills'] = self.get_skills()
        candidate_info['skills_num'] = self.get_skills_length(candidate_info['skills'])

        if self.keywords:
            candidate_info['skills_match'] = self.check_skills(candidate_info['skills'])

        return candidate_info

    # Assign different number of points for different sections and calculate cv fullness
    def get_score(self) -> int:
        """
        Calculates the completeness score of a candidate's resume.

        Returns:
        int: The completeness score.
        """

        prof_info = (WebDriverWait(self.driver, 20).
                     until(EC.presence_of_element_located((By.TAG_NAME, 'alliance-employer-resume-prof-info'))))

        # Get the number of filled sections in the resume
        h3 = len(prof_info.find_elements(By.TAG_NAME, 'h3'))
        h4 = len(prof_info.find_elements(By.TAG_NAME, 'h4'))
        p = len(prof_info.find_elements(By.TAG_NAME, 'p'))
        ul = len(prof_info.find_elements(By.TAG_NAME, 'ul'))

        main_info = len((self.driver.find_element(By.TAG_NAME, 'alliance-employer-resume-brief-info').
                         find_elements(By.TAG_NAME, 'p')))

        cv_fullness = h3 * 4 + h4 * 4 + p * 0.2 + ul * 0.2 + main_info * 5

        return int(cv_fullness)

    def get_skills(self) -> str:
        """
        Extracts skills information from candidate profiles.

        Returns:
        str: The skills' information.
        """

        skills_elm = (WebDriverWait(self.driver, 10).
                      until(EC.presence_of_element_located((By.TAG_NAME,
                                                            'alliance-shared-ui-prof-resume-skill-summary'))))
        skills = skills_elm.text.replace('\n', ' ').replace('ключова інформація', '')

        return skills if len(skills) != 0 else 'not specified'

    @staticmethod
    def get_skills_length(skills: str) -> Union[int, str]:
        """
        Gets the length of skills information.

        Parameters:
        - skills (str): The skills' information.

        Returns:
        Union[int, str]: The length of skills information or 'not specified'.
        """

        return len(skills) if skills != 'not specified' else 0

    def check_skills(self, skills: str) -> int:
        """
        Checks how many keywords match the skills information.

        Parameters:
        - skills (str): The skills' information.

        Returns:
        int: The number of keywords matched.
        """

        match = 0
        for word in self.keywords:
            if word.lower() in skills.lower():
                match += 1
        return match

    def upload_to_json(self) -> None:
        """Uploads the parsed candidate information to a JSON file."""

        with open('candidates.json', 'w', encoding="utf-8") as json_file:
            json.dump(self.result, json_file, ensure_ascii=False, indent=4)
            print('Resumes was download successfully!')
