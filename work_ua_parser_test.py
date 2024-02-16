from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

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
#
# url = 'https://www.work.ua/resumes/?ss=1'
# # url = 'https://www.work.ua/resumes/9125228/'
# url = 'https://www.work.ua/resumes-dnipro-data+scientist/?employment=75&experience=166'
url = 'https://www.work.ua/resumes-kyiv-data+scientist/?education=66&experience=165'
driver.get(url)

salary_min_elm = driver.find_element(By.ID, 'salaryfrom_selection')


salary_min_list = salary_min_elm.find_elements(By.TAG_NAME, 'option')


# [print(val.text) for val in salary_min_list]
exp_salary = 3000

salary_min_elm.click()
for elm in salary_min_list[1:]:
    salary = int(''.join([val for val in elm.text[:7] if val.isdigit()]))
    if exp_salary >= salary:
        salary_min_elm.send_keys(salary)
        sleep(3)

driver.refresh()

salary_max_elm = driver.find_element(By.ID, 'salaryto_selection')
salary_max_list = salary_max_elm.find_elements(By.TAG_NAME, 'option')

salary_max_elm.click()
for elm in salary_max_list[1:]:
    salary = int(''.join([val for val in elm.text[:7] if val.isdigit()]))
    if exp_salary >= salary:
        salary_max_elm.send_keys(salary)
        sleep(3)







