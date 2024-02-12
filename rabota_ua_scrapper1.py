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
from concurrent.futures import ThreadPoolExecutor


options = webdriver.ChromeOptions()
options.add_argument("--window-size=1366,768")
# options.add_argument("--blink-settings=imagesEnabled=false")
options.add_argument('--headless=new')


# url = 'https://robota.ua/ru/candidates/all/ukraine'
# url = 'https://robota.ua/ru/candidates/data-analyst/ukraine?salary=%7B%22from%22%3A50%2C%22to%22%3Anull%7D'
# url = 'https://robota.ua/ru/candidates/data-scientist/ukraine?salary=%7B%22from%22%3A50%2C%22to%22%3Anull%7D'
# url = 'https://robota.ua/ru/candidates/python-developer/kyiv'
# url = 'https://robota.ua/candidates/22121161'
# url = 'https://robota.ua/candidates/23012131'
# url = 'https://robota.ua/candidates/20202674'
# url = 'https://robota.ua/candidates/23196247'
# url = 'https://robota.ua/candidates/22711696'
# url = 'https://robota.ua/candidates/22867203'
url = 'https://robota.ua/candidates/23012131'
# url = 'https://robota.ua/candidates/23018283'
# url = 'https://robota.ua/candidates/23061108'

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                          options=options)
driver.implicitly_wait(10)
actions = ActionChains(driver)
driver.get(url)

def extract_data(lst):
    res = []
    info = {}
    h4 = lst.find_elements(By.TAG_NAME, 'h4')
    data = lst.find_elements(By.TAG_NAME, 'p')
    if not data:
        data = lst.find_elements(By.TAG_NAME, 'ul')

    for header in h4:
        print(header.text)
        for text in data:
            print(text.text)

        # res.append(text.text)

    return res


prof_info = driver.find_element(By.TAG_NAME, 'alliance-employer-resume-prof-info')
# exp_info = driver.find_element(By.TAG_NAME, 'alliance-shared-ui-prof-resume-experience')
# skills = driver.find_element(By.TAG_NAME, 'alliance-shared-ui-prof-resume-skill-summary')
#
# education = driver.find_element(By.TAG_NAME, 'alliance-shared-ui-prof-resume-education')
# courses = driver.find_element(By.TAG_NAME, 'alliance-shared-ui-prof-resume-courses')
# add_info = driver.find_element(By.TAG_NAME, 'alliance-shared-ui-prof-resume-additional')

# main_info = driver.find_element(By.TAG_NAME, 'alliance-employer-resume-brief-info')
# brief_info = main_info.find_elements(By.TAG_NAME, 'p')
# city = brief_info[0].text
# age = 'not specified'
# if len(brief_info) > 1


# print(city, age)


# print(skills.text)
# for info in brief_info:
#     print(info.text)
#
# cv = {}
# if len(brief_info) < 3:
#     city, age = brief_info
#     salary = 0
# else:
#     city, salary, age = brief_info
#     salary = salary.text
#
# cv['city'] = city.text
# cv['expected_salary'] = salary
# cv['age'] = age.text
#
# print(cv)

# key_info = driver.find_element(By.XPATH, "*//[contain(text(), 'Ключова інформация')]")
# print(key_info)

headers_h3 = prof_info.find_elements(By.TAG_NAME, 'h3')
headers_h4 = prof_info.find_elements(By.TAG_NAME, 'h4')
p = prof_info.find_elements(By.TAG_NAME, 'p')
ul = prof_info.find_elements(By.TAG_NAME, 'ul')
# print(add_info.text)

current_window_handle = driver.current_window_handle
handles = driver.window_handles

# print(handles)

# print(extract_data(exp_info))
# print(extract_data(skills))
# print(extract_data(education))
# print(extract_data(courses))
# print(extract_data(add_info))
# print(p.text)
# [print(len(t.text)) for t in p]
# for text in headers:
#     print(text.text)
# print(f'HEADERS H3: {len(headers_h3)}')
# for head in headers_h3:
#     for head.find_elements(By.TAG_NAME, 'p').text in head:
#         print(f"{head.text}: {head.find_element(By.TAG_NAME, 'p').text}")
# print(f'HEADERS H4: {len(headers_h4)}')

# print(f'PARAGRAPHS: {len(p)}')
# cv_fullnes = len(headers_h3) * 5 + len(headers_h4) * 4 + len(p) * 0.2 + len(ul) * 0.2
# print(int(cv_fullnes))

# h3 - 5 points
# h4 - 2 points
# p - 1 point