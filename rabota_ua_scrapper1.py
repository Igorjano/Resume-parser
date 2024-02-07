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
options.add_argument("--blink-settings=imagesEnabled=false")
options.add_argument('--headless=new')


# url = 'https://robota.ua/ru/candidates/all/ukraine'
# url = 'https://robota.ua/ru/candidates/data-analyst/ukraine?salary=%7B%22from%22%3A50%2C%22to%22%3Anull%7D'
# url = 'https://robota.ua/ru/candidates/data-scientist/ukraine?salary=%7B%22from%22%3A50%2C%22to%22%3Anull%7D'
# url = 'https://robota.ua/ru/candidates/python-developer/kyiv'
# url = 'https://robota.ua/candidates/22121161'
# url = 'https://robota.ua/candidates/23012131'
# url = 'https://robota.ua/candidates/20202674'
# url = 'https://robota.ua/candidates/23196247'
url = 'https://robota.ua/candidates/22711696'

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                          options=options)
driver.implicitly_wait(10)
actions = ActionChains(driver)
driver.get(url)

name = driver.find_element(By.CLASS_NAME, 'santa-typo-h2')


resume_info = driver.find_element(By.TAG_NAME, 'alliance-employer-resume-prof-info').text
print(resume_info)
cv_fullness = (len(resume_info) * 100) / 1650
print(cv_fullness)
print(len(resume_info))
# print(name.tex)



