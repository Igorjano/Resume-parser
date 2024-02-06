from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

# def get_cv_link(cv_elements):
#     # cv_elements = driver.find_elements(By.CLASS_NAME, 'cv-card')
#     print('CV-ELEMENTS')
#     for cv in cv_elements:
#         position = cv.find_element(By.CLASS_NAME, 'santa-m-0').text
#         cv_page = cv.find_element(By.CLASS_NAME, 'santa-no-underline').get_attribute("href")
#         print(position)
#         print(cv_page)

options = webdriver.ChromeOptions()
options.add_argument("--window-size=1366,768")
options.add_argument("--blink-settings=imagesEnabled=false")
options.add_argument('--headless=new')

# url = 'https://robota.ua/ru/candidates/all/ukraine'
# url = 'https://robota.ua/ru/candidates/data-analyst/ukraine?salary=%7B%22from%22%3A50%2C%22to%22%3Anull%7D'
# url = 'https://robota.ua/ru/candidates/data-scientist/ukraine?salary=%7B%22from%22%3A50%2C%22to%22%3Anull%7D'
# url = 'https://robota.ua/ru/candidates/python-developer/kyiv'
# url = 'https://robota.ua/candidates/22121161'
url = 'https://robota.ua/candidates/23012131'
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                          options=options)
driver.implicitly_wait(10)
actions = ActionChains(driver)
driver.get(url)

# driver.find_element(By.CLASS_NAME, 'additional-no-x-indent').click()
# filters_btn.click()
# sleep(2)


def get_score(cv):
    try:
        score_text = cv.find_element(By.TAG_NAME, 'alliance-fillable-resume').text
        # print(score_text)
        score = ''
        for let in score_text:
            score += let if let.isnumeric() else ''
            # if let.isnumeric():
            #     score += let
        score = int(score)
    except NoSuchElementException:
        score = 0
    return score


# filters_cont = driver.find_element(By.CLASS_NAME, 'filter-panel-container')
keywords = ['IT', 'SQLite', 'Наука', 'HTML', 'PostgreSQL', 'Retail']

# cv_elements = driver.find_elements(By.CLASS_NAME, 'cv-card')
# print(len(cv_elements))
# for cv in cv_elements:
#     position = cv.find_element(By.CLASS_NAME, 'santa-m-0').text
#     cv_page = cv.find_element(By.CLASS_NAME, 'santa-no-underline').get_attribute("href")
#     score = get_score(cv)
#     try:
    #     score_text = cv.find_element(By., 'alliance-fillable-resume').text
    # except NoSuchElementException:
    # score = self.get_score(score_text)
    # self.get_cv_info(cv_page, score)
    # print(position)
    # print(score)
    # print(cv_page)


name = (driver.find_element(By.CLASS_NAME, 'santa-flex-grow').
        find_element(By.TAG_NAME, 'h1').text)
position = driver.find_element(By.CLASS_NAME, 'santa-mt-10').text
#
# brief_info = driver.find_element(By.TAG_NAME, 'alliance-employer-resume-brief-info')
# city, age, salary = brief_info.find_elements(By.TAG_NAME, 'p')
# city = city.text
# age = age.text
# salary = salary.text
#
print(name)
print(position)
# print(city)
# print(age)
# print(salary)

experience_field = (driver.find_element(By.TAG_NAME, 'alliance-shared-ui-prof-resume-experience').
                    find_element(By.TAG_NAME, 'p')).text

try:
    skills = (driver.find_element(By.TAG_NAME, 'alliance-shared-ui-prof-resume-skill-summary').
              find_element(By.CLASS_NAME, 'santa-m-0').text)
    skills_match = 0
    for key in keywords:
        if key in skills:
            skills_match += 1
            print(key)
    print(skills_match)
except NoSuchElementException:
    skills_match = 0

print(experience_field)
print(skills)

# def show_all_checkboxes(self):
#     filters = self.driver.find_element(By.CLASS_NAME, 'filters-sidebar')
#     self.scroll_screen()
#     add_btns = filters.find_elements(By.TAG_NAME, 'button')
#     [btn.click() for btn in add_btns]
#     sleep(2)
#     self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
#
#
# def set_checkboxes(self, keywords):
#     self.show_all_checkboxes()
#     filters_elm = self.driver.find_elements(By.TAG_NAME, 'alliance-employer-cvdb-simple-rubric')
#     list_elm = self.driver.find_elements(By.CLASS_NAME, 'list-item')
#     for lst in list_elm:
#         try:
#             lst.find_element(By.TAG_NAME, 'santa-checkbox').click()
#             print(f'Click {lst.text}')
#         except ElementNotInteractableException:
#             print(f'No click {lst.text}')
#             continue
#     # print(len(list_elm))
#     # filters_elm = self.driver.find_elements(By.CLASS_NAME, 'list-item')
#     # [x.click() for x in filters_elm if x.text in keywords]
#     # checkboxes = filters_elm.find_element(By.TAG_NAME, 'input')
#     # for box in filters_elm:
#     #     box.find_element(By.TAG_NAME, 'input').click()
#     # [box.click() for box in checkboxes]
#
#     # [x.click() for x in checkboxes_elm if x.text in keywords]





