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
        self.url = 'https://robota.ua/candidates/all'
        self.result = []
        self.keywords = None
        self.position = None
        self.location = None
        self.years_of_exp = None
        self.salary_min = None
        self.salary_min = None
        self.salary_max = None
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--window-size=1366,768")
        # self.options.add_argument("--blink-settings=imagesEnabled=false")
        # self.options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                       options=self.options)
        self.driver.implicitly_wait(10)

    def parse(self):
        self.driver.get(self.url)
        self.tune_options()
        self.set_position()
        self.set_location()
        self.set_experience()
        self.set_salary()
        sleep(5)
        try:
            pages_elm = self.driver.find_element(By.CLASS_NAME, 'paginator')
            pages_links = pages_elm.find_elements(By.TAG_NAME, 'a')
            if len(pages_links) > 5:
                print(len(pages_links))
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
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                next_page = self.driver.find_element(By.CLASS_NAME, 'next')
                print(f"{next_page.get_attribute('href') = }")
                sleep(1)
                next_page.click()
                sleep(1)
                print('click')
                print('CLICK NEXT PAGE')
            except NoSuchElementException:
                print('EXCEPTION IS WORKING')
                print('STOP')
                next_page = False
        print(self.result)
        self.driver.quit()
        self.upload_results()
        return self.result

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
        print('GET CV LINKS ELEMENTS')
        cv_elements = self.driver.find_elements(By.CLASS_NAME, 'cv-card')
        print('GET LINKS')
        links = [elm.find_element(By.CSS_SELECTOR, 'a').get_attribute("href") for elm in cv_elements]
        print('OPEN NEW TABS')

        current_window_handle = self.driver.current_window_handle
        self.driver.execute_script("window.open('');")
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[1])

        # with ThreadPoolExecutor(max_workers=25) as executor:
        #     executor.map(self.get_cv_data, links)

        for link in links:
            self.get_cv_data(link)
        self.driver.close()
        self.driver.switch_to.window(current_window_handle)

    def get_cv_data(self, page_link):
        self.driver.get(page_link)
        print('CV CARD')
        cv_info = {}
        print(f'GET LINK {page_link}')
        cv_info['name'] = self.driver.find_element(By.CLASS_NAME, 'santa-typo-h2').text
        cv_info['position'] = (self.driver.find_element(By.TAG_NAME, 'lib-resume-main-info').
                               find_element(By.CLASS_NAME, 'santa-typo-secondary ')).text
        cv_info['city'] = (self.driver.find_element(By.TAG_NAME, 'alliance-employer-resume-brief-info').
                           find_element(By.TAG_NAME, 'p')).text
        cv_info['page'] = page_link

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
                      find_element(By.CLASS_NAME, 'santa-sentence-case').text)
            for key in self.keywords:
                if key in skills:
                    print(key)
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

    def tune_options(self):
        print('Please enter search parameters. If you want to leave fields empty just press Enter')
        position = input('Job position:\t')
        if position != '':
            self.position = position

        location = input('Location:\t')
        if location != '':
            self.location = location

        years_of_exp = input('If you want only candidates without experience enter 0. Years of experience:\t')
        if years_of_exp != '':
            self.years_of_exp = self.validate(years_of_exp)

        keywords = (input('Enter skills or keywords separated by commas or press Enter:\t')
                    .capitalize().split(','))
        if keywords != ['']:
            self.keywords = keywords

        salary_min = input('Enter min salary expected:\t')
        if salary_min != '':
            self.salary_min = self.validate(salary_min)

        salary_max = input('Enter max salary expected:\t')
        if salary_max != '':
            self.salary_max = self.validate(salary_max)

        photos = input('Enter yes/no to show resumes with photo only:\t')
        if photos == 'yes':
            self.show_photo()

    def set_position(self):
        if self.position:
            job_search = self.driver.find_element(By.TAG_NAME, 'santa-suggest-input')
            job_input = job_search.find_element(By.TAG_NAME, 'input')
            job_input.send_keys(self.position)
            job_input.send_keys(Keys.RETURN)

    def set_location(self):
        if self.location:
            loc_search = self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-desktop-filter-city')
            loc_search.click()
            loc_search.find_element(By.TAG_NAME, 'input').send_keys(self.location)
            try:
                loc_search.find_element(By.TAG_NAME, 'li').click()
            except StaleElementReferenceException as e:
                print('EXCEPT SET LOCATION')
                print(e.args)

    def set_experience(self):
        if self.years_of_exp:
            filters_elm = self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-simple-experience')
            list_elm = filters_elm.find_elements(By.CLASS_NAME, 'list-item')
            for checkbox in list_elm:
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
        self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
        self.driver.find_element(By.TAG_NAME, 'santa-toggler').click()

    def upload_results(self):
        with open('robota_ua_candidates.json', 'w', encoding='utf8') as json_file:
            json.dump(self.result, json_file, indent=4, ensure_ascii=False)
        print('Data were received successfully')


p = RobotaUaParser()
p.parse()



