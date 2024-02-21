from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from time import sleep
import json


class WorkUaParser:
    def __init__(self):
        self.url = 'https://www.work.ua/resumes/?ss=1'
        self.result = []
        self.keywords = None
        self.location = None
        self.years_of_exp = None
        self.salary_min = None
        self.salary_min = None
        self.salary_max = None
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--blink-settings=imagesEnabled=false')
        # self.options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                       options=self.options)

    def parse(self):
        self.driver.get(self.url)
        self.set_options()
        print('Downloading resume ...')
        self.get_number_of_cv()

        next_btn = True
        while next_btn:
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

    def get_cv_links(self):
        try:
            cv_elms = (WebDriverWait(self.driver, 20).
                       until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'resume-link'))))

            links = [WebDriverWait(elm, 10).
                     until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a'))).
                     get_attribute("href") for elm in cv_elms]

            current_window_handle = self.driver.current_window_handle

            for link in links:
                self.driver.execute_script("window.open('');")
                handles = self.driver.window_handles
                self.driver.switch_to.window(handles[1])
                self.get_cv_data(link)
                self.driver.close()
                self.driver.switch_to.window(current_window_handle)

            print(f'{len(self.result)} candidates was downloaded')

        except TimeoutException:
            print('There are no candidates according to the given criteria')

    def get_cv_data(self, page_link):
        self.driver.get(page_link)
        candidate_info = {}

        cv_card_elm = (WebDriverWait(self.driver, 10).
                       until(EC.presence_of_element_located((By.CLASS_NAME, 'card'))))

        candidate_info['position'] = cv_card_elm.find_element(By.TAG_NAME, 'h2').text
        candidate_info['name'] = cv_card_elm.find_element(By.TAG_NAME, 'h1').text
        candidate_info['cv_page'] = page_link
        candidate_info['cv_fullness'] = self.get_score()
        candidate_info['skills'], candidate_info['skills_num'] = self.get_skills()

        if self.keywords:
            candidate_info['skill_match'] = self.check_skills(candidate_info['skills'])
        self.result.append(candidate_info)

    def get_skills(self):
        try:
            skills_elm = (WebDriverWait(self.driver, 10).
                          until(EC.presence_of_element_located((By.CLASS_NAME, 'card'))))

            skills = skills_elm.find_elements(By.CLASS_NAME, 'flex')[1].text.replace('\n', ', ')
            skills_num = len(skills)
        except IndexError:
            skills = 'not specified'
            skills_num = 0

        return skills, skills_num

    def check_skills(self, skills):
        match = 0
        for word in self.keywords:
            if word.lower() in skills.lower():
                match += 1
        return match

    def get_score(self):
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

    def set_options(self):
        print('Setting options ...')
        self.set_category()
        self.select_options()
        self.set_location()
        self.set_experience()
        self.set_salary()
        self.set_salary('max')
        print('Searching ...')
        sleep(1)

    def set_category(self):
        category = input('Choose category in what you want to search:\n1 - Job position\n2 - Skills or keywords\t')
        if category == '1':
            search_text = input('What position are you looking for:\t')
            self.set_search_text(search_text)
        elif category == '2':
            self.switch_category()
            search_text = input('What skills are you looking for:\t')
            self.keywords = search_text.split()
            self.set_search_text(search_text)
        else:
            print('Please make your choice')
            self.set_category()

    def set_search_text(self, text):
        search_input = (WebDriverWait(self.driver, 20).
                        until(EC.visibility_of_element_located((By.CLASS_NAME, 'form-control'))))

        search_input.send_keys(text)
        search_input.send_keys(Keys.RETURN)
        sleep(1)

    # Switch category for search everywhere on the text
    def switch_category(self):
        (WebDriverWait(self.driver, 20).
         until(EC.element_to_be_clickable((By.ID, 'f1-1')))).click()
        sleep(1)

        (WebDriverWait(self.driver, 20).
         until(EC.element_to_be_clickable((By.ID, 'f3-3')))).click()
        sleep(1)

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
            try:
                loc_search = (WebDriverWait(self.driver, 20).
                              until(EC.element_to_be_clickable((By.ID, 'city'))))
                loc_search.send_keys(Keys.CONTROL, 'a')
                loc_search.send_keys(Keys.DELETE)
                loc_search.send_keys(self.location)
                loc_search.send_keys(Keys.RETURN)
                loc_search.send_keys(Keys.RETURN)
                sleep(1)
            except TimeoutException:
                print('You enter the wrong location! Location set to all Ukraine')

    def set_experience(self):
        if self.years_of_exp:
            try:
                exp_elms = (WebDriverWait(self.driver, 20).
                            until(EC.visibility_of_element_located((By.ID, 'experience_selection'))))

                checkboxes = (WebDriverWait(exp_elms, 20).
                              until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'checkbox'))))

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

    def set_salary(self, max_=None):
        self.driver.refresh()
        try:
            if not max_:
                salary_elm = (WebDriverWait(self.driver, 20).
                              until(EC.presence_of_element_located((By.ID, 'salaryfrom_selection'))))

                salary = self.salary_min
            else:
                salary_elm = (WebDriverWait(self.driver, 20).
                              until(EC.presence_of_element_located((By.ID, 'salaryto_selection'))))

                salary = self.salary_max
            if salary:
                salary_list = (WebDriverWait(salary_elm, 10).
                               until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'option'))))
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

    @staticmethod
    def validate(value):
        while not type(value) is int:
            try:
                value = int(value)
            except ValueError:
                value = input('Enter integer number:\t')
        return value

    def show_photo(self):
        (WebDriverWait(self.driver, 20).
         until(EC.element_to_be_clickable((By.ID, 'photo_selection')))).click()
        sleep(1)

    def get_number_of_cv(self):
        number_elm = (WebDriverWait(self.driver, 20).
                      until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))).text

        number = ''.join([num for num in number_elm if num.isdigit()])
        print(f'Was found {number} candidate(-tes)')

    def upload_to_json(self):
        with open('candidates.json', 'w', encoding="utf-8") as json_file:
            json.dump(self.result, json_file, ensure_ascii=False, indent=4)
        print('Resume was download successfully!')
