from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import List, Dict, Optional, Union
import json


class WorkUaParser:
    """
    WorkUaParser is a class for parsing candidate information from the Work.ua website.

    Attributes:
    - url (str): The URL of the Work.ua resumes page.
    - result (list): A list to store all parsed candidates' information.
    - keywords (list): A list of keywords to match with candidate skills.
    - category (str): The category of the search.
    - search_text (str): The search text or keywords.
    - location (Optional[str]): Name of the city to filter candidates.
    - years_of_exp (Optional[int]): The minimum years of experience required for candidates.
    - salary_min (Optional[int]): The minimum salary expected for candidates.
    - salary_max (Optional[int]): The maximum salary expected for candidates.
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
        Initializes the WorkUaParser object.

        Parameters:
        - category (str): The category of the search.
        - text (str): The search text or keywords.
        - location (Optional[str]): Name of the city to filter candidates.
        - experience (Optional[int]): The minimum years of experience required for candidates.
        - salary_min (Optional[int]): The minimum salary expected for candidates.
        - salary_max (Optional[int]): The maximum salary expected for candidates.
        - photo (bool): Flag to include candidate photos in the results.
        """

        self.url = 'https://www.work.ua/resumes/?ss=1'
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
        self.options.add_argument('--start-maximized')
        self.options.add_argument("--blink-settings=imagesEnabled=false")
        self.options.add_argument("--blink-settings=imagesEnabled=false")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        # self.options.add_argument('--headless=new')
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

        while True:
            self.get_cv_links()
            try:
                next_btn = (self.driver.find_element(By.CLASS_NAME, 'pagination').
                            find_element(By.CLASS_NAME, 'add-left-default'))

                next_btn_link = next_btn.find_element(By.TAG_NAME, 'a').get_attribute('href')
                self.driver.get(next_btn_link)

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
                      until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))).text

        number = ''.join([num for num in number_elm if num.isdigit()])
        print(f'Was found {number} candidate(-tes)')

        return number

    def set_options(self) -> None:
        """Sets options for the parser."""

        print('Setting options ...')
        self.set_category()
        self.set_location()
        self.set_experience()
        self.set_salary()
        self.set_salary('max')
        self.show_photo()
        print('Searching ...')
        sleep(1)

    def set_category(self) -> None:
        """Sets the category based on the provided input (job position or keywords)."""

        if self.category == '1':
            self.set_search_text(self.search_text)
        elif self.category == '2':
            self.switch_category()
            self.keywords = self.search_text.split()
            self.set_search_text(self.search_text)

    # Switch category for search everywhere on the text
    def switch_category(self) -> None:
        """Switches the category in the search mode."""

        # self.driver.refresh()
        (WebDriverWait(self.driver, 20).
         until(EC.element_to_be_clickable((By.ID, 'f1-1')))).click()
        sleep(1)

        (WebDriverWait(self.driver, 20).
         until(EC.element_to_be_clickable((By.ID, 'f3-3')))).click()
        sleep(1)

    def set_search_text(self, text) -> None:
        """
        Sets the search text in the input field.

        Parameters:
        - text (str): The search text or keywords.
        """

        search_input = (WebDriverWait(self.driver, 20).
                        until(EC.visibility_of_element_located((By.CLASS_NAME, 'form-control'))))

        search_input.send_keys(text)
        search_input.send_keys(Keys.RETURN)
        sleep(1)

    def set_location(self) -> None:
        """Sets the name of the city to filter candidates."""

        if self.location:
            try:
                loc_search = (WebDriverWait(self.driver, 10).
                              until(EC.element_to_be_clickable((By.ID, 'city'))))

                loc_search.send_keys(Keys.CONTROL, 'a')
                loc_search.send_keys(Keys.DELETE)
                loc_search.send_keys(self.location)
                loc_search.send_keys(Keys.RETURN)
                loc_search.send_keys(Keys.RETURN)
                sleep(1)

            except TimeoutException:
                print('You enter the wrong location! Location set to all Ukraine')

    def set_experience(self) -> None:
        """Sets the experience filter for candidates."""

        if self.years_of_exp:
            try:
                exp_elms = (WebDriverWait(self.driver, 20).
                            until(EC.presence_of_element_located((By.ID, 'experience_selection'))))

                checkboxes = (WebDriverWait(exp_elms, 20).
                              until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'checkbox'))))

                if self.years_of_exp == 0:
                    checkboxes[0].click()
                elif self.years_of_exp < 1:
                    checkboxes[1].click()
                elif 1 <= self.years_of_exp < 2:
                    checkboxes[2].click()
                elif 2 <= self.years_of_exp < 5:
                    checkboxes[3].click()
                elif self.years_of_exp >= 5:
                    checkboxes[4].click()
                sleep(1)
            except TimeoutException:
                print('There are some trouble. Experience was not set')

    def set_salary(self, field=None) -> None:
        """Sets the salary range filter for candidates."""

        self.driver.refresh()
        try:
            if not field:
                salary_elm = (WebDriverWait(self.driver, 20).
                              until(EC.presence_of_element_located((By.ID, 'salaryfrom_selection'))))

                salary = self.salary_min
            else:
                salary_elm = (WebDriverWait(self.driver, 20).
                              until(EC.presence_of_element_located((By.ID, 'salaryto_selection'))))

                salary = self.salary_max
            if salary:
                salary_list = (WebDriverWait(salary_elm, 20).
                               until(EC.presence_of_all_elements_located((By.TAG_NAME, 'option'))))
                salary_elm.click()
                sleep(1)

                prev_salary = 0
                for i, elm in enumerate(salary_list[1:]):
                    # Get available values of salary on this parameters
                    salary_from_list = int(''.join([val for val in elm.text[:7] if val.isdigit()]))
                    if prev_salary <= salary < salary_from_list:
                        # Choose salary from the list
                        salary_list[i].click()
                        break
                    prev_salary = salary_from_list
        except NoSuchElementException:
            print('You enter the wrong salary! Salary was not set')

    def show_photo(self) -> None:
        """Sets the visibility of candidate photos."""

        if self.photo:
            (WebDriverWait(self.driver, 20).
             until(EC.element_to_be_clickable((By.ID, 'photo_selection')))).click()

    def get_cv_links(self) -> None:
        """Gets the links to individual candidate profiles."""

        try:
            cv_elms = (WebDriverWait(self.driver, 20).
                       until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'resume-link'))))

            links = [WebDriverWait(elm, 10).
                     until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a'))).
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

        Parameters:
        - page_link (str): The URL of the candidate's profile page.

        Returns:
        dict: Dictionary containing candidate information.
        """

        candidate_info = {}

        cv_card_elm = (WebDriverWait(self.driver, 10).
                       until(EC.presence_of_element_located((By.CLASS_NAME, 'card'))))

        candidate_info['position'] = cv_card_elm.find_element(By.TAG_NAME, 'h2').text
        candidate_info['name'] = cv_card_elm.find_element(By.TAG_NAME, 'h1').text
        candidate_info['cv_page'] = self.driver.current_url
        candidate_info['cv_fullness'] = self.get_score()
        candidate_info['skills'] = self.get_skills()
        candidate_info['skills_num'] = self.get_skills_length(candidate_info['skills'])

        if self.keywords:
            candidate_info['skills_match'] = self.check_skills(candidate_info['skills'])

        return candidate_info

    def get_score(self) -> int:
        """
        Calculates the completeness score of a candidate's resume.

        Returns:
        int: The completeness score.
        """

        # Get the number of filled sections in the summary
        cv_info = (WebDriverWait(self.driver, 10).
                   until(EC.presence_of_element_located((By.CLASS_NAME, 'card'))))

        headers = len(cv_info.find_elements(By.TAG_NAME, 'h2'))
        paragraphs = len(cv_info.find_elements(By.TAG_NAME, 'p'))

        brief_info = len(cv_info.find_element(By.CLASS_NAME, 'dl-horizontal').
                         find_elements(By.TAG_NAME, 'dd'))

        # Assign different numbers of points for different sections and calculate cv fullness
        cv_fullness = headers * 2 + paragraphs * 1 + brief_info * 5

        # Check if a resume was added there
        try:
            if self.driver.find_element(By.CLASS_NAME, 'resume-preview'):
                cv_fullness += 20
        except NoSuchElementException:
            pass

        return int(cv_fullness)

    def get_skills(self) -> str:
        """
        Extracts skills information from candidate profiles.

        Returns:
        str: The skills' information.
        """

        try:
            skills_elm = (WebDriverWait(self.driver, 10).
                      until(EC.presence_of_element_located((By.CLASS_NAME, 'card'))))

            skills = skills_elm.find_elements(By.CLASS_NAME, 'flex')[1].text.replace('\n', ', ')
        except IndexError:
            skills = 'not specified'

        return skills

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

    def check_skills(self, skills) -> int:
        """
        Checks how many keywords match the skills information.

        Parameters:
        - skills (str): The skills information.

        Returns:
        int: The number of keywords matched.
        """

        match = 0
        for word in self.keywords:
            if word.lower() in skills.lower():
                match += 1
        return match

    def upload_to_json(self):
        """Uploads the parsed candidate information to a JSON file."""

        with open('candidates.json', 'w', encoding="utf-8") as json_file:
            json.dump(self.result, json_file, ensure_ascii=False, indent=4)
        print('Resume was download successfully!')
