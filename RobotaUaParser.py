from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from time import sleep


class RobotaUaParser:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--window-size=1366,768")
        # self.options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                       options=self.options)

    def parse(self, url):
        self.driver.get(url)
        self.select_options()
        sleep(3)
        # while True:
        #     self.get_cv_link()
        #     try:
        #         next_page = self.driver.find_element(By.CLASS_NAME, 'next')
        #         next_page.click()
        #         time.sleep(1)
        #         print('click')
        #     except NoSuchElementException:
        #         print('EXCEPTION IS WORKING')
        #         print('STOP')
        #         break

    def scroll_screen(self):
        for i in range(0, 4000, 500):
            self.driver.execute_script(f"window.scrollTo({i}, {i + 500});")

    def get_cv_link(self):
        cv_elements = self.driver.find_elements(By.CLASS_NAME, 'cv-card')
        for cv in cv_elements:
            position = cv.find_element(By.CLASS_NAME, 'santa-m-0').text
            cv_page = cv.find_element(By.CLASS_NAME, 'santa-no-underline').get_attribute("href")
            get_candidate_info()
            print(position)
            print(cv_page)

    def select_options(self):
        # print('Please enter search parameters. If you want to leave fields empty just press Enter')
        # position = input('Job position:\t')
        position = 'Python developer'
        if position:
            self.set_position(position)
        # location = input('Location:\t')
        location = 'Киев'
        if location:
            self.set_location(location)
        # keywords = input('Enter skills or keywords separated by commas:\t').capitalize().split(',')
        keywords = ['IT', 'Development', 'Наука', 'Продажи', 'Банки', 'Транспорт и логистика']
        # print(keywords)
        # if keywords:
        #     self.set_checkboxes(keywords)
        years_of_exp = 7
        # years_of_exp = input('If you want candidates without experience enter 0. Years of experience:\t')
        if years_of_exp:
            years_of_exp = self.validate(years_of_exp)
            self.set_experience(years_of_exp)
        salary_min = 25000
        salary_max = 60000
        if salary_min or salary_max:
            self.validate(salary_min)
            self.validate(salary_max)
            self.set_salary(salary_min, salary_max)
        language = 'English'
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
                value = input('Enter the integer number:\t')
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
        sleep(1)
        loc_search.find_element(By.TAG_NAME, 'li').click()
        sleep(2)

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
                    if experience > 10:
                        checkbox.find_element(By.TAG_NAME, 'santa-checkbox').click()
            else:
                if int(years[0]) <= experience < int(years[1]):
                    checkbox.find_element(By.TAG_NAME, 'santa-checkbox').click()

    def set_salary(self, salary_min, salary_max):
        range_elm = self.driver.find_element(By.TAG_NAME, 'alliance-employer-cvdb-simple-salary')
        input_elm = range_elm.find_element(By.TAG_NAME, 'lib-input-range')
        min_input, max_input = input_elm.find_elements(By.TAG_NAME, 'input')
        min_input.send_keys(salary_min)
        sleep(1)
        min_input.send_keys(Keys.RETURN)
        max_input.send_keys(salary_max)
        sleep(1)
        max_input.send_keys(Keys.RETURN)
        sleep(5)

    def show_photo(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
        self.driver.find_element(By.TAG_NAME, 'santa-toggler').click()




    def show_all_checkboxes(self):
        filters = self.driver.find_element(By.CLASS_NAME, 'filters-sidebar')
        self.scroll_screen()
        add_btns = filters.find_elements(By.TAG_NAME, 'button')
        [btn.click() for btn in add_btns]
        sleep(2)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")

    def set_checkboxes(self, keywords):
        self.show_all_checkboxes()
        filters_elm = self.driver.find_elements(By.TAG_NAME, 'alliance-employer-cvdb-simple-rubric')
        list_elm = self.driver.find_elements(By.CLASS_NAME, 'list-item')
        for lst in list_elm:
            try:
                lst.find_element(By.TAG_NAME, 'santa-checkbox').click()
                print(f'Click {lst.text}')
            except ElementNotInteractableException:
                print(f'No click {lst.text}')
                continue
        # print(len(list_elm))
        # filters_elm = self.driver.find_elements(By.CLASS_NAME, 'list-item')
        # [x.click() for x in filters_elm if x.text in keywords]
        # checkboxes = filters_elm.find_element(By.TAG_NAME, 'input')
        # for box in filters_elm:
        #     box.find_element(By.TAG_NAME, 'input').click()
            # [box.click() for box in checkboxes]

        # [x.click() for x in checkboxes_elm if x.text in keywords]



url = 'https://robota.ua/ru/candidates/all/ukraine'

p = RobotaUaParser()
p.parse(url)




# print(p.validate('grgr'))