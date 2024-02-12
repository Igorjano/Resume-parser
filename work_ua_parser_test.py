from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep


options = webdriver.ChromeOptions()
options.add_argument("--window-size=1366,768")
# options.add_argument("--blink-settings=imagesEnabled=false")
# options.add_argument('--headless=new')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                          options=options)
driver.implicitly_wait(10)

url = 'https://www.work.ua/resumes/?ss=1'
# url = 'https://www.work.ua/resumes/9125228/'

driver.get(url)

pages_links = driver.find_elements(By.TAG_NAME, 'nav')[-1]
next_btn = pages_links.find_element(By.CLASS_NAME, 'add-left-default').click()
sleep(2)

# print(next_btn.text)
# [print(page.text) for page in next_btn]


# cv_info = driver.find_element(By.CLASS_NAME, 'card')
#
# name = cv_info.find_element(By.TAG_NAME, 'h1')
# print(name.text)
#
# position = cv_info.find_element(By.TAG_NAME, 'h2')
# print(position.text)

# headers = cv_info.find_elements(By.TAG_NAME, 'h2')
# for header in headers:
#     print(header.find_elements(By.CLASS_NAME, 'h4'))

# [print(header.text) for header in headers]


# city_age = cv_info.find_element(By.CLASS_NAME, 'dl-horizontal').find_elements(By.TAG_NAME, 'dd')
# lines = len(city_age)
# age = city_age[(lines - 3)].text
# city = city_age[(lines - 2)].text
#
# print(f'{age = }, {city = }')
#
# skills = cv_info.find_elements(By.CLASS_NAME, 'flex')[1].text.strip()
# # print(skills)



