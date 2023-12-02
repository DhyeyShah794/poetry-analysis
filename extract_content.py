# Remove unnecessary imports later
import pandas
import csv
import itertools
import collections
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
import re

# Uncomment to create the poem_urls_combined.csv file. To be refactored
# with open('poem_urls.csv', 'r') as f:
#     data = f.read()
    # urls = [row.split(',')[0] for row in data.split('\n')]
    # urls = urls[1:]
    # print(len(urls))
    # print(len(set(urls)))

    # url_category = {}
    # rows = data.split('\n')[1:]
    # for row in rows:
    #     url, category = row.split(',')
    #     url_category.setdefault(url, []).append(category)
    # with open('poem_urls_combined.csv', 'w', newline='') as csv_file:
    #     writer = csv.writer(csv_file)
    #     for url, categories in url_category.items():
    #         writer.writerow([url, categories])


def navigate_to(driver, url):  # Need to import from scrape.py instead of duplicating
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    get_url = driver.current_url
    wait.until(EC.url_to_be(url))
    if get_url == url:
        page_source = driver.page_source
        return page_source
    else:
        return None


def perform_login(driver, username, password):  # Same as above
    time.sleep(2)
    email_field = driver.find_element(By.ID, "user_name")
    password_field = driver.find_element(By.ID, "user_password")
    email_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)


with open("poem_urls_combined.csv", 'r') as f:
    # TODO: Refactor this and put it in a well-documented function
    base_url = "https://allpoetry.com/"
    data = f.read()
    rows = data.split('\n')
    urls = [row.split(',')[0] for row in rows[35_600:35_650]]
    driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    navigate_to(driver, base_url + "/login")
    time.sleep(2)
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")
    perform_login(driver, username, password)
    time.sleep(2)
    for url in urls:
        driver.get(url)
        titles = driver.find_elements(By.CSS_SELECTOR, "a.nocolor.fn")
        title_url = url.replace(base_url, '/')
        href = f"[href='{title_url}']"
        titles += driver.find_elements(By.CSS_SELECTOR, href)
        print(list(set([title.text for title in titles if title.text != ""]))[0])
    driver.close()
