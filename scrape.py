from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import getpass
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import codecs

driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def navigate_to(driver, url):
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    get_url = driver.current_url
    wait.until(EC.url_to_be(url))
    if get_url == url:
        page_source = driver.page_source
        return page_source
    else:
        return None


def get_categories(driver):
    all_link = driver.find_element(By.LINK_TEXT, "All »")
    all_link.click()
    all_categories = driver.find_element(By.CLASS_NAME, "all_cats")
    all_categories_a = all_categories.find_elements(By.TAG_NAME, "a")
    return [a.text for a in all_categories_a]


def perform_login(driver, username, password):
    time.sleep(2)
    email_field = driver.find_element(By.ID, "user_name")
    password_field = driver.find_element(By.ID, "user_password")
    email_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

def get_poem_urls(driver, category):
    test_url = base_url + f"/poems/about/{category}"
    navigate_to(driver, test_url)
    for i in range(100):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    for i in range(6000):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        current = driver.find_elements(By.CSS_SELECTOR, "em.current")
        if len(current) > 0 and current[-1].text == "80":
            break

    titles_a = driver.find_elements(By.CSS_SELECTOR, "a.nocolor.fn")
    hrefs = [a.get_attribute("href") for a in titles_a]

    file = codecs.open("poem_urls.txt", "a+")
    for href in hrefs:
        file.write(href + "\n")
    file.close()


base_url = "https://allpoetry.com/"
navigate_to(driver, base_url)
categories = get_categories(driver)

login_url = base_url + "/login"
navigate_to(driver, login_url)

username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")

perform_login(driver, username, password)
for category in categories:
    get_poem_urls(driver, category)

driver.quit()
