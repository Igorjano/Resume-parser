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
# options.add_argument('--headless=new')

# url = 'https://robota.ua/ru/candidates/all/ukraine'
# url = 'https://robota.ua/ru/candidates/data-analyst/ukraine?salary=%7B%22from%22%3A50%2C%22to%22%3Anull%7D'
url = 'https://robota.ua/ru/candidates/data-scientist/ukraine?salary=%7B%22from%22%3A50%2C%22to%22%3Anull%7D'

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                          options=options)
actions = ActionChains(driver)
driver.get(url)

# driver.find_element(By.CLASS_NAME, 'additional-no-x-indent').click()
# filters_btn.click()
# time.sleep(5)


# filters_cont = driver.find_element(By.CLASS_NAME, 'filter-panel-container')
url = 'https://robota.ua/ru/candidates/data-analyst/ukraine?salary=%7B%22from%22%3A50%2C%22to%22%3Anull%7D'
driver.get(url)
keywords = ['IT', 'Банки', 'Наука', 'Интернет', 'Юридические услуги', 'Retail']

# filters = driver.find_element(By.CLASS_NAME, 'filters-sidebar')
switcher = driver.find_element(By.TAG_NAME, 'santa-toggler')
# switcher = photo_elm.find_element(By.TAG_NAME, 'input')
# sleep(1)
switcher.click()
sleep(3)












