import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import json
from time import sleep
from concurrent.futures import ThreadPoolExecutor


class RobotaUaParser:
    def __init__(self):
        self.result = []
        self.keywords = None
        self.url = 'https://robota.ua/candidates/all'
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--window-size=1366,768")
        # self.options.add_argument("--blink-settings=imagesEnabled=false")
        # self.options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                       options=self.options)
        self.driver.implicitly_wait(10)

    # def __call__(self):
    #     self.parse()

    def parse(self):
        self.driver.get(self.url)
        print('GET URL')
        self.select_options()
        try:
            pages_elm = self.driver.find_element(By.CLASS_NAME, 'paginator')
            print(F'PAGES ELM = {pages_elm}')
            pages_links = pages_elm.find_elements(By.TAG_NAME, 'a')
            print(len)
            if len(pages_links) > 5:
                print('PARSE NEXT PAGES')
                self.parse_next_page()
            else:
                print('PARSE PAGES')
                self.parse_pages()
        except NoSuchElementException:
            print('EXCEPTION')
            self.get_cv_links()
        finally:
            print(self.result)
            self.driver.quit()
            self.upload_results()
            return self.result

    # If we have more than 5 pages and next button
    def parse_next_page(self):
        next_page = True
        while next_page:
            try:
                self.get_cv_links()
                next_page = self.driver.find_element(By.CLASS_NAME, 'next')
                next_page.click()
                print('click')
                print('CLICK NEXT PAGE')
            except NoSuchElementException:
                print('EXCEPTION IS WORKING')
                print('STOP')
                next_page = False

    def parse_pages(self):
        pages_elm = self.driver.find_element(By.CLASS_NAME, 'paginator').find_elements(By.TAG_NAME, 'a')
        pages = [page.get_attribute('href') for page in pages_elm]
        print(pages)
        print(pages[0])
        print(f'PARSE PAGE {pages[0]}')
        self.get_cv_links()
        print('PAGE WAS PARSED')
        count = 1
        for page in pages[1:]:
            print(f'PARSE PAGE {page}')
            self.driver.get(page)
            self.get_cv_links()

    def get_cv_links(self):
        cv_elements = self.driver.find_elements(By.CLASS_NAME, 'cv-card')
        print(cv_elements)

        links = [elm.find_element(By.CSS_SELECTOR, 'a').get_attribute("href") for elm in cv_elements]
        print(links)

        current_window_handle = self.driver.current_window_handle
        self.driver.execute_script("window.open('');")
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[1])

        # with ThreadPoolExecutor(max_workers=25) as executor:
        #     executor.map(self.get_cv_data, links)

        for link in links:
            self.get_cv_data(link)
            # self.driver.close()
        self.driver.switch_to.window(current_window_handle)

    def get_cv_data(self, page_link):
        self.driver.get(page_link)
        print('CV CARD')
        cv_info = {}
        print(f'GET LINK {page_link}')
        cv_info['position'] = (self.driver.find_element(By.TAG_NAME, 'lib-resume-main-info').
                               find_element(By.CLASS_NAME, 'santa-typo-secondary ')).text
        cv_info['page'] = page_link
        cv_info['name'] = self.driver.find_element(By.CLASS_NAME, 'santa-typo-h2').text
        cv_info['city'] = (self.driver.find_element(By.TAG_NAME, 'alliance-employer-resume-brief-info').
                           find_element(By.TAG_NAME, 'p')).text
        # age_elm = (self.driver.find_element(By.TAG_NAME, 'alliance-employer-resume-brief-info').
        #            find_elements(By.TAG_NAME, 'span'))
        # cv_info['age'] = age_elm[1]
        if self.keywords:
            skills_match = self.check_skills()
            if skills_match:
                print('CHECK SKILLS')
                cv_info['key_match'] = skills_match
                self.result.append(cv_info)
        else:
            self.result.append(cv_info)

    def check_skills(self):
        try:
            skills_match = 0
            skills = (self.driver.find_element(By.TAG_NAME, 'alliance-shared-ui-prof-resume-skill-summary').
                      find_element(By.CLASS_NAME, 'santa-m-0').text)
            for key in self.keywords:
                if key in skills:
                    skills_match += 1
            return skills_match
        except NoSuchElementException:
            return 0

    @staticmethod
    def get_numbers(cv):
        try:
            score_text = cv.find_element(By.TAG_NAME, 'alliance-fillable-resume').text
            if any(char.isdigit() for char in score_text):
                score = ''.join(num for num in score_text if num.isdigit())
                return int(score)
        except NoSuchElementException:
            return 0

    def select_options(self):
        pass
        # print('Please enter search parameters. If you want to leave fields empty just press Enter')
        # position = input('Job position:\t')
        position = 'data analyst'
        if position:
            self.set_position(position)
        # location = input('Location:\t')
        location = 'Киев'
        if location:
            self.set_location(location)
        # self.keywords = (input('Enter skills or keywords separated by commas or press Enter:\t')
        #                  .capitalize().split(','))
        self.keywords = ['IT', 'Django', 'Наука', 'Postgres', 'SQL', 'Big data']
        years_of_exp = 10
        # years_of_exp = input('If you want only candidates without experience enter 0. Years of experience:\t')
        if years_of_exp:
            years_of_exp = self.validate(years_of_exp)
            self.set_experience(years_of_exp)
        # salary_min = 20000
        # salary_max = 60000
        # if salary_min or salary_max:
        #     self.validate(salary_min)
        #     self.validate(salary_max)
        #     self.set_salary(salary_min, salary_max)
        # photos = input('Enter yes/no to show resumes with photo only:\t'
        photo = 'yes'
        if photo == 'yes':
            self.show_photo()

    @staticmethod
    def validate(value):
        while not type(value) is int:
            try:
                value = int(value)
            except ValueError:
                value = input('Enter integer number:\t')
        return value

    def set_position(self, position):
        job_search = self.driver.find_element(By.TAG_NAME, 'santa-suggest-input')
        job_input = job_search.find_element(By.TAG_NAME, 'input')
        job_input.send_keys(position)
        job_input.send_keys(Keys.RETURN)

    def set_location(self, location):
        loc_search = self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-desktop-filter-city')
        loc_search.click()
        loc_search.find_element(By.TAG_NAME, 'input').send_keys(location)
        loc_search.find_element(By.TAG_NAME, 'li').click()

    def set_experience(self, experience):
        filters_elm = self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-simple-experience')
        list_elm = filters_elm.find_elements(By.CLASS_NAME, 'list-item')
        for checkbox in list_elm:
            text_lbl = checkbox.find_element(By.TAG_NAME, 'p')
            years = [y for y in text_lbl.text.split() if y.isdigit()]
            if not len(years):
                if experience == 0:
                    checkbox.find_element(By.TAG_NAME, 'santa-checkbox').click()
            elif len(years) == 1:
                if years[0] == '1':
                    if experience < 1:
                        checkbox.find_element(By.TAG_NAME, 'santa-checkbox').click()
                elif years[0] == '10':
                    if experience >= 10:
                        checkbox.find_element(By.TAG_NAME, 'santa-checkbox').click()
            else:
                if int(years[0]) <= experience < int(years[1]):
                    checkbox.find_element(By.TAG_NAME, 'santa-checkbox').click()

    def set_salary(self, salary_min, salary_max):
        range_elm = self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-simple-salary')
        input_elm = range_elm.find_element(By.TAG_NAME, 'lib-input-range')
        min_input, max_input = input_elm.find_elements(By.TAG_NAME, 'input')
        min_input.send_keys(salary_min)
        min_input.send_keys(Keys.RETURN)
        max_input.send_keys(salary_max)
        max_input.send_keys(Keys.RETURN)

    def show_photo(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
        self.driver.find_element(By.TAG_NAME, 'santa-toggler').click()

    def upload_results(self):
        with open('robota_ua_candidates.json', 'w', encoding='utf8') as json_file:
            json.dump(self.result, json_file, indent=4, ensure_ascii=False)
        print('Data were received successfully')



# url = 'https://robota.ua/candidates/data-analyst/ukraine'
# url = 'https://robota.ua/candidates/data-scientist/ukraine'
# url = 'https://robota.ua/ua/candidates/data-scientist/ukraine?experienceIds=%5B%224%22%5D'


# p = RobotaUaParser()
# p.parse()



