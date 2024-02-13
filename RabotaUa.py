import json
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from time import sleep


class RobotaUaParser:
    def __init__(self):
        self.url = 'https://robota.ua/candidates/all'
        self.result = []
        self.candidate_info = {}
        self.keywords = []
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
        print('Downloading resumes ...')
        try:
            pages = (self. driver.find_element(By.CLASS_NAME, 'paginator').
                     find_elements(By.TAG_NAME, 'a'))
            if len(pages) == 6:
                self.parse_next_btn()
            else:
                self.parse_pages()
        except NoSuchElementException as e:
            print(e.msg)
            print('PAGINATOR EXCEPTION')
            self.get_cv_links()
            self.driver.quit()
            self.upload_to_json()
        except TimeoutException as e:
            print(e.msg)
            print('Ops! Something wrong with the server')

    # If we have more than 5 pages and next button
    def parse_next_btn(self):
        print('PARSE NEXT BUTTON')
        next_btn = True
        while next_btn:
            try:
                # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                next_btn = (WebDriverWait(self.driver, 20).
                            until(EC.visibility_of_element_located((By.CLASS_NAME, 'next'))))
                # print(f"{next_btn.get_attribute('href') = }")
                next_btn.click()
                self.get_cv_links()
            except NoSuchElementException as e:
                print(e.msg)
                print('NEXT PAGE EXCEPTION')
                next_page = False
            except TimeoutException as e:
                print(e.msg)
                next_page = False

        self.upload_to_json()

        print(self.result)
        self.driver.quit()
        # self.upload_results()
        return self.result

    def parse_pages(self):
        # print('PARSE PAGES')
        pages_links = (self.driver.find_element(By.CLASS_NAME, 'paginator').
                       find_elements(By.TAG_NAME, 'a'))
        self.get_cv_links()
        for page in pages_links[1:]:
            # print(f'PARSE PAGE {page}')
            page.click()
            self.get_cv_links()
        self.driver.quit()
        self.upload_to_json()

    def get_cv_links(self):
        try:
            # print('GET CV LINKS')
            cv_elms = (WebDriverWait(self.driver, 20).
                       until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'cv-card'))))
            links = [elm.find_element(By.CSS_SELECTOR, 'a').get_attribute("href") for elm in cv_elms]

            current_window_handle = self.driver.current_window_handle

            for link in links:
                self.driver.execute_script("window.open('');")
                handles = self.driver.window_handles
                self.driver.switch_to.window(handles[1])
                self.get_cv_data(link)
                self.driver.close()
                self.driver.switch_to.window(current_window_handle)
        except NoSuchElementException as e:
            print(e.msg)
            print('GET CV LINKS EXCEPTION')
            print('There are no candidates according to the given criteria')
        except TimeoutException as e:
            print(e.msg)
            print('Ops! Something wrong with the server')

    def get_cv_data(self, page_link):
        self.driver.get(page_link)

        print(f'OPEN {page_link}')

        candidate_info = {}
        position_elm = (WebDriverWait(self.driver, 20).
                        until(EC.presence_of_element_located((By.TAG_NAME, 'lib-resume-main-info'))))
        candidate_info['position'] = (position_elm.
                                      find_element(By.CLASS_NAME, 'santa-typo-secondary ')).text
        candidate_info['name'] = self.driver.find_element(By.CLASS_NAME, 'santa-typo-h2').text
        candidate_info['cv_fullness'] = self.get_score()
        candidate_info['cv_page'] = page_link
        candidate_info['skills'] = self.get_skills()
        if self.keywords:
            candidate_info['skills_match'] = self.check_skills(candidate_info['skills'])
        # print(candidate_info)
        self.result.append(candidate_info)

    def get_score(self):
        prof_info = self.driver.find_element(By.TAG_NAME, 'alliance-employer-resume-prof-info')

        # Get the number of filled sections in the summary
        h3 = len(prof_info.find_elements(By.TAG_NAME, 'h3'))
        h4 = len(prof_info.find_elements(By.TAG_NAME, 'h4'))
        p = len(prof_info.find_elements(By.TAG_NAME, 'p'))
        ul = len(prof_info.find_elements(By.TAG_NAME, 'ul'))
        main_info = len((self.driver.find_element(By.TAG_NAME, 'alliance-employer-resume-brief-info').
                         find_elements(By.TAG_NAME, 'p')))

        # Assign different numbers of points for different sections and calculate cv fullness
        cv_fullness = h3 * 4 + h4 * 4 + p * 0.2 + ul * 0.2 + main_info * 5

        return int(cv_fullness)

    def get_skills(self):
        skills = (self.driver.find_element(By.TAG_NAME, 'alliance-shared-ui-prof-resume-skill-summary').text
                  .replace('\n', ' ').replace('ключова інформація', ''))
        if skills == '':
            skills = 'not specified'

        return skills

    def check_skills(self, skills):
        match = 0
        for word in self.keywords:
            if word.capitalize() in skills:
                match += 1
                print(word)
        return match

    def set_options(self):
        print('Setting options ...')
        self.set_category()
        self.select_options()
        self.set_location()
        self.set_experience()
        self.set_salary()
        sleep(1)

    def set_category(self):
        category = input('Choose category in what you want to search:\n1 - Job position\n2 - Skills or keywords\t')
        # category = '1'
        search_text = 'Data analyst'
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

    def switch_category(self):
        category_list = self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-desktop-search-mode')
        category_list.click()

        try:
            category = category_list.find_elements(By.TAG_NAME, 'p')
            category[4].click()
        except StaleElementReferenceException as e:
            print('CATEGORY EXCEPTION')
            print(e.msg)

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
                    until(EC.element_to_be_clickable((By.TAG_NAME, 'alliance-employer-cvdb-desktop-filter-city'))))
            loc_search.click()
            loc_search.find_element(By.TAG_NAME, 'input').send_keys(self.location)
            sleep(2)
            try:
                loc_search.find_element(By.TAG_NAME, 'li').click()
            except StaleElementReferenceException as e:
                print('EXCEPT SET LOCATION')
                print(e.msg)

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

    @staticmethod
    def exception_error():
        print('Something went wrong... Please try again')

    def upload_to_json(self):
        with open('candidates_robota_ua.json', 'w', encoding="utf-8") as json_file:
            json.dump(self.result, json_file, ensure_ascii=False, indent=4)
        print('Resumes was received successfully!')


p = RobotaUaParser()
p.parse()