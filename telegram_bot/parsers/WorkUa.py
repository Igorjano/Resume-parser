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


class WorkUaParser:
    def __init__(self, category, text, location, experience, salary_min, salary_max, photo):
        self.url = 'https://www.work.ua/resumes/?ss=1'
        self.result = []
        self.keywords = None
        self.category = category
        self.search_text = text
        self.location = location
        self.years_of_exp = experience
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.photo = photo
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--window-size=1366,768")
        self.options.add_argument("--blink-settings=imagesEnabled=false")
        self.options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                       options=self.options)

    def parse(self):
        self.driver.get(self.url)
        self.set_options()
        self.get_number_of_cv()
        print('Downloading resume ...')
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
            links = [elm.find_element(By.CSS_SELECTOR, 'a').get_attribute("href") for elm in cv_elms]
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

    def get_cv_data(self, page_link):
        self.driver.get(page_link)
        candidate_info = {}

        candidate_info['position'] = self.driver.find_element(By.TAG_NAME, 'h2').text
        candidate_info['name'] = self.driver.find_element(By.TAG_NAME, 'h1').text
        candidate_info['cv_page'] = page_link
        candidate_info['cv_fullness'] = self.get_score()
        candidate_info['skills'], candidate_info['skills_num'] = self.get_skills()
        if self.keywords:
            candidate_info['skill_match'] = self.check_skills(candidate_info['skills'])
        self.result.append(candidate_info)

    def get_skills(self):
        try:
            skills = (self.driver.find_element(By.CLASS_NAME, 'card').
                      find_elements(By.CLASS_NAME, 'flex')[1].text.replace('\n', ', '))
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
        cv_info = self.driver.find_element(By.CLASS_NAME, 'card')
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
        self.set_category()
        print('Setting options ...')
        self.set_location()
        self.set_experience()
        self.set_salary()
        self.set_salary('max')
        self.show_photo()
        print('Searching ...')
        sleep(1)

    def set_category(self):
        if self.category == '1':
            self.set_search_text(self.search_text)
        elif self.category == '2':
            self.switch_category()
            self.keywords = self.search_text.split()
            self.set_search_text(self.search_text)

    def set_search_text(self, text):
        search_input = self.driver.find_element(By.CLASS_NAME, 'form-control')
        search_input.send_keys(text)
        search_input.send_keys(Keys.RETURN)
        sleep(1)

    # Switch category for search everywhere on the text
    def switch_category(self):
        for i in range(3):
            filter_elm = (WebDriverWait(self.driver, 20).
                          until(EC.presence_of_element_located((By.CLASS_NAME, 'filters-controls-container'))))
            search_elms = filter_elm.find_elements(By.CLASS_NAME, 'form-group')[-1]
            checkboxes = search_elms.find_elements(By.CLASS_NAME, 'checkbox')
            checkboxes[i].click()
            sleep(1)

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
            except NoSuchElementException:
                print('You enter the wrong location! Location set to all Ukraine')
            except StaleElementReferenceException:
                print('Something went wrong... Please try again')

    def set_experience(self):
        if self.years_of_exp:
            try:
                exp_elms = (self.driver.find_element(By.ID, 'experience_selection').
                            find_elements(By.CLASS_NAME, 'checkbox'))
                if self.years_of_exp == 0:
                    exp_elms[0].click()
                elif self.years_of_exp < 1:
                    exp_elms[1].click()
                elif 1 <= self.years_of_exp < 2:
                    exp_elms[2].click()
                elif 2 <= self.years_of_exp < 5:
                    exp_elms[3].click()
                elif self.years_of_exp >= 5:
                    exp_elms[4].click()
                sleep(1)
            except (NoSuchElementException, StaleElementReferenceException):
                print('There are some trouble. Experience was not set')

    def set_salary(self, field=None):
        self.driver.refresh()
        if not field:
            salary_elm = self.driver.find_element(By.ID, 'salaryfrom_selection')
            salary = self.salary_min
        else:
            salary_elm = self.driver.find_element(By.ID, 'salaryto_selection')
            salary = self.salary_max
        if salary:
            salary_list = salary_elm.find_elements(By.TAG_NAME, 'option')
            salary_elm.click()

            prev_salary = 0
            for i, elm in enumerate(salary_list[1:]):
                # Get available values of salary on this parameters
                salary_from_list = int(''.join([val for val in elm.text[:7] if val.isdigit()]))
                if prev_salary <= salary < salary_from_list:
                    # Choose salary from the list
                    salary_list[i].click()
                    break
                prev_salary = salary_from_list

    def show_photo(self):
        if self.photo:
            self.driver.find_element(By.ID, 'photo_selection').click()

    def get_number_of_cv(self):
        number_elm = self.driver.find_element(By.TAG_NAME, 'h1').text
        number = ''.join([num for num in number_elm if num.isdigit()])
        if number == '0':
            print('There are no candidates according to the given criteria')
            self.driver.quit()
        print(f'Was found {number} candidate(-tes)')

    def upload_to_json(self):
        with open('candidates.json', 'w', encoding="utf-8") as json_file:
            json.dump(self.result, json_file, ensure_ascii=False, indent=4)
        print('Resumes was download successfully!')
