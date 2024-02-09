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
import json
from time import sleep
from concurrent.futures import ThreadPoolExecutor


class RobotaUaParser:
    def __init__(self):
        self.url = 'https://robota.ua/candidates/all'
        self.result = []
        self.candidate_info = {}
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
        self.set_options()

        try:
            pages_links = (WebDriverWait(self.driver, 20).
                           until(EC.presence_of_element_located((By.CLASS_NAME, 'paginator'))))
            pages = pages_links.find_elements(By.TAG_NAME, 'a')
            if len(pages) > 5:
                print(len(pages))
                print('PARSE NEXT PAGES')
                self.parse_next_btn()
        except (NoSuchElementException, TimeoutException) as e:
            print(e.msg)
            self.get_cv_links()
            print(self.result)
            self.driver.quit()
            # self.upload_results()
            print(self.result)
            return self.result

    # If we have more than 5 pages and next button
    def parse_next_btn(self):
        next_page = True
        while next_page:
            self.get_cv_links()

            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                next_page = (WebDriverWait(self.driver, 20).
                             until(EC.presence_of_element_located((By.CLASS_NAME, 'next'))))
                print(f"{next_page.get_attribute('href') = }")
                next_page.click()
                sleep(1)
                print('click')
                print('CLICK NEXT PAGE')
            except NoSuchElementException as e:
                print(e.msg)
                print('NEXT PAGE EXCEPTION')
                next_page = False

        print(self.result)
        self.driver.quit()
        # self.upload_results()
        return self.result

    def parse_pages(self):
        pages_links = (WebDriverWait(self.driver, 20).
                       until(EC.presence_of_element_located((By.CLASS_NAME, 'paginator'))))
        pages_elm = pages_links.find_elements(By.TAG_NAME, 'a')
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
        cv_elm = (WebDriverWait(self.driver, 20).
                  until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'cv-card'))))
        print('GET LINKS')
        links = [elm.find_element(By.CSS_SELECTOR, 'a').get_attribute("href") for elm in cv_elm]
        print('OPEN NEW TABS')

        current_window_handle = self.driver.current_window_handle
        self.driver.execute_script("window.open('');")
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[1])

        with ThreadPoolExecutor(max_workers=25) as executor:
            executor.map(self.get_cv_data, links)

        # for link in links:
        #     self.get_cv_data(link)
            self.driver.close()
            self.driver.switch_to.window(current_window_handle)

    def get_cv_data(self, page_link):
        self.driver.get(page_link)
        print('CV CARD')
        print(f'GET LINK {page_link}')
        # city, salary, age = self.get_brief_info()
        cv_fullness = self.get_score()
        skills = self.get_skills()
        self.candidate_info['position'] = (self.driver.find_element(By.TAG_NAME, 'lib-resume-main-info').
                                           find_element(By.CLASS_NAME, 'santa-typo-secondary ')).text
        self.candidate_info['name'] = self.driver.find_element(By.CLASS_NAME, 'santa-typo-h2').text
        # self.candidate_info['city'] = city
        # self.candidate_info['expected_salary'] = salary
        # self.candidate_info['age'] = age
        self.candidate_info['cv_fullness'] = cv_fullness
        self.candidate_info['cv_page'] = page_link
        self.candidate_info['skills'] = skills
        self.result.append(self.candidate_info)
        print(self.candidate_info)
        # print(self.result)
        self.candidate_info.clear()
        # print(self.result)

    # def get_brief_info(self):
        brief_info = (self.driver.find_element(By.TAG_NAME, 'alliance-employer-resume-brief-info').
                      find_elements(By.TAG_NAME, 'p'))
        if len(brief_info) < 3:
            city, age = brief_info
            salary = 0
        else:
            city, salary, age = brief_info
            salary = salary.text
        return city, salary, age

    def get_score(self):
        prof_info = self.driver.find_element(By.TAG_NAME, 'alliance-employer-resume-prof-info')
        headers_h3 = prof_info.find_elements(By.TAG_NAME, 'h3')
        headers_h4 = prof_info.find_elements(By.TAG_NAME, 'h4')
        p = prof_info.find_elements(By.TAG_NAME, 'p')
        ul = prof_info.find_elements(By.TAG_NAME, 'ul')

        cv_fullness = len(headers_h3) * 5 + len(headers_h4) * 4 + len(p) * 0.2 + len(ul) * 0.2

        return cv_fullness

    def get_skills(self):
        skills_elm = self.driver.find_element(By.TAG_NAME, 'alliance-shared-ui-prof-resume-skill-summary')
        skills = skills_elm.find_elements(By.TAG_NAME, 'p')
        if not skills:
            skills = skills_elm.find_elements(By.TAG_NAME, 'ul')

        return [[].append(skill) for skill in skills]

    def set_options(self):
        self.set_category()
        self.select_options()
        self.set_location()
        self.set_experience()
        self.set_salary()
        sleep(5)

    def set_category(self):
        category = input('Choose category in what you want to search:\n1 - CV name\n2 - skills or keywords\t')
        # category = '2'
        # search_text = 'Python developer'
        if category == '1':
            search_text = input('What position are you looking for:\t')
            self.set_search_text(search_text)
        elif category == '2':
            search_text = input('What skills are you looking for:\t')
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
            loc_search = self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-desktop-filter-city')
            loc_search.click()
            loc_search.find_element(By.TAG_NAME, 'input').send_keys(self.location)
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

p = RobotaUaParser()
p.parse()
