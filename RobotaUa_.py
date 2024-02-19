from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from time import sleep
import json
from sys import exit


class RobotaUaParser:
    def __init__(self):
        self.url = 'https://robota.ua/candidates/all'
        self.result = []
        self.candidate_info = {}
        self.keywords = None
        self.location = None
        self.years_of_exp = None
        self.salary_min = None
        self.salary_min = None
        self.salary_max = None
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--window-size=1366,768")
        self.options.add_argument("--blink-settings=imagesEnabled=false")
        # self.options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                       options=self.options)

    def parse(self):
        self.driver.get(self.url)
        self.set_options()
        self.get_number_of_cv()
        print('Downloading resume ...')
        try:
            self.get_cv_links()
            pages = (self. driver.find_element(By.CLASS_NAME, 'paginator').
                     find_elements(By.TAG_NAME, 'a'))
            if len(pages) > 5:
                self.parse_next_btn()
            else:
                self.parse_pages(len(pages))
        except NoSuchElementException:
            self.driver.quit()
            self.upload_to_json()
            return self.result
        except TimeoutException:
            print('Ops! Something wrong with the server')

    # If we have more than 5 pages use next button for navigation
    def parse_next_btn(self):
        next_btn = True
        while next_btn:
            try:
                next_btn = (WebDriverWait(self.driver, 20).
                            until(EC.visibility_of_element_located((By.CLASS_NAME, 'next'))))
                print(f"{next_btn.get_attribute('href') = }")
                next_btn.click()
                self.get_cv_links()
            except (NoSuchElementException, TimeoutException):
                next_btn = False

        self.driver.quit()
        self.upload_to_json()
        return self.result

    # Click on every next page link
    def parse_pages(self, number):
        for i in range(number - 1):
            pages_links = (self.driver.find_element(By.CLASS_NAME, 'paginator').
                           find_elements(By.TAG_NAME, 'a'))
            pages_links[i + 1].click()
            sleep(1)
            self.get_cv_links()
        self.driver.quit()
        self.upload_to_json()
        return self.result

    def get_cv_links(self):
        try:
            cv_elms = (WebDriverWait(self.driver, 20).
                       until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'cv-card'))))
            links = [elm.find_element(By.TAG_NAME, 'a').get_attribute("href") for elm in cv_elms]
            current_window_handle = self.driver.current_window_handle

            for link in links:
                self.driver.execute_script("window.open('');")
                handles = self.driver.window_handles
                self.driver.switch_to.window(handles[1])
                self.get_cv_data(link)
                self.driver.close()
                self.driver.switch_to.window(current_window_handle)
        except NoSuchElementException:
            print('Oops! Something went wrong .. Try again')
            self.driver.quit()
        except TimeoutException:
            print('There are no candidates according to the given criteria')
            self.driver.quit()
            exit()

    def get_cv_data(self, page_link):
        self.driver.get(page_link)
        candidate_info = {}

        position_elm = (WebDriverWait(self.driver, 20).
                        until(EC.presence_of_element_located((By.TAG_NAME, 'lib-resume-main-info'))))
        candidate_info['position'] = (position_elm.
                                      find_element(By.CLASS_NAME, 'santa-typo-secondary ')).text
        candidate_info['name'] = self.driver.find_element(By.CLASS_NAME, 'santa-typo-h2').text
        candidate_info['cv_page'] = page_link
        candidate_info['cv_fullness'] = self.get_score()
        candidate_info['skills'], candidate_info['skills_num'] = self.get_skills()
        if self.keywords:
            candidate_info['skills_match'] = self.check_skills(candidate_info['skills'])
        self.result.append(candidate_info)

    # Assign different number of points for different sections and calculate cv fullness
    def get_score(self):
        prof_info = self.driver.find_element(By.TAG_NAME, 'alliance-employer-resume-prof-info')

        # Get the number of filled sections in the resume
        h3 = len(prof_info.find_elements(By.TAG_NAME, 'h3'))
        h4 = len(prof_info.find_elements(By.TAG_NAME, 'h4'))
        p = len(prof_info.find_elements(By.TAG_NAME, 'p'))
        ul = len(prof_info.find_elements(By.TAG_NAME, 'ul'))
        main_info = len((self.driver.find_element(By.TAG_NAME, 'alliance-employer-resume-brief-info').
                         find_elements(By.TAG_NAME, 'p')))

        cv_fullness = h3 * 4 + h4 * 4 + p * 0.2 + ul * 0.2 + main_info * 5

        return int(cv_fullness)

    def get_skills(self):
        skills = (self.driver.find_element(By.TAG_NAME, 'alliance-shared-ui-prof-resume-skill-summary').text
                  .replace('\n', ' ').replace('ключова інформація', ''))
        skills_num = len(skills)
        if skills == '':
            skills = 'not specified'
            skills_num = 0

        return skills, skills_num

    def check_skills(self, skills):
        match = 0
        for word in self.keywords:
            if word.lower() in skills.lower():
                match += 1
        return match

    def set_options(self):
        self.set_category()
        self.select_options()
        print('Setting options ...')
        self.set_location()
        self.set_experience()
        self.set_salary()
        print('Searching ...')
        sleep(1)

    def set_category(self):
        category = input('Choose category in what you want to search:\n1 - Job position\n2 - Skills or keywords\t')
        if category == '1':
            search_text = input('What position are you looking for:\t')
            self.set_search_text(search_text)
        elif category == '2':
            search_text = input('What skills are you looking for:\t')
            self.keywords = search_text.split()
            self.switch_category()
            self.set_search_text(search_text)
        else:
            print('Please make your choice')
            self.set_category()

    def set_search_text(self, text):
        search_input = (self.driver.find_element(By.TAG_NAME, 'santa-suggest-input')
                        .find_element(By.TAG_NAME, 'input'))
        search_input.send_keys(text)
        search_input.send_keys(Keys.RETURN)
        sleep(1)

    # Switch category of search for Skills section
    def switch_category(self):
        category_list = self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-desktop-search-mode')
        category_list.click()

        try:
            category = category_list.find_elements(By.TAG_NAME, 'p')
            category[4].click()
        except StaleElementReferenceException:
            print('Something wrong with the category')

    def select_options(self):
        print('Please enter search additional parameters. If you want to leave fields empty just press Enter')

        location = input('Location:\t')
        if location != '':
            self.location = location

        years_of_exp = input('If you want only candidates without experience enter 0. Years of experience:\t')
        if years_of_exp != '':
            self.years_of_exp = self.validate(years_of_exp)

        salary_min = input('Enter min salary expected:\t')
        if salary_min != '':
            self.salary_min = self.validate(salary_min)
        salary_max = input('Enter max salary expected:\t')
        if salary_max != '':
            self.salary_max = self.validate(salary_max)

        photos = input('Enter yes/no to show resumes with photo only:\t')
        if photos == 'yes':
            self.show_photo()

    def set_location(self):
        if self.location:
            loc_search = (WebDriverWait(self.driver, 20).
                          until(EC.element_to_be_clickable((By.TAG_NAME,
                                                            'alliance-employer-cvdb-desktop-filter-city'))))
            loc_search.click()
            loc_search.find_element(By.TAG_NAME, 'input').send_keys(self.location)
            sleep(2)
            try:
                loc_search.find_element(By.TAG_NAME, 'li').click()
            except StaleElementReferenceException:
                print('Something went wrong... Please try again')
            except NoSuchElementException:
                print('You enter the wrong location! Location set to all Ukraine')

    def set_experience(self):
        if self.years_of_exp:
            filters_elm = self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-simple-experience')
            list_elm = filters_elm.find_elements(By.CLASS_NAME, 'list-item')
            for checkbox in list_elm:
                # Get the label of checkboxes because it changes dynamically
                text_lbl = checkbox.find_element(By.TAG_NAME, 'p')
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

    def set_salary(self):
        range_elm = self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-simple-salary')
        input_elm = range_elm.find_element(By.TAG_NAME, 'lib-input-range')
        min_input, max_input = input_elm.find_elements(By.TAG_NAME, 'input')

        if self.salary_min:
            min_input.send_keys(self.salary_min)
            min_input.send_keys(Keys.RETURN)
        if self.salary_max:
            max_input.send_keys(self.salary_max)
            max_input.send_keys(Keys.RETURN)

    @staticmethod
    def validate(value):
        while not type(value) is int:
            try:
                value = int(value)
            except ValueError:
                value = input('Enter integer number:\t')
        return value

    def show_photo(self):
        sleep(2)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
        self.driver.find_element(By.TAG_NAME, 'santa-toggler').click()

    def get_number_of_cv(self):
        number = (self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-search-header').
                  find_element(By.CLASS_NAME, 'santa-text-red-500')).text
        print(f'Was found {number} candidate(-tes)')
        if number == '0':
            print('There are no candidates according to the given criteria')
            self.driver.quit()
            exit()

    def upload_to_json(self):
        with open('candidates.json', 'w', encoding="utf-8") as json_file:
            json.dump(self.result, json_file, ensure_ascii=False, indent=4)
            print('Resumes was download successfully!')

