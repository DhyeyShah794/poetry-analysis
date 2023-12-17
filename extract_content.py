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
import os
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import codecs
import re
from scrape import get_target_categories, navigate_to, perform_login


if not os.path.exists('poem_urls_combined.csv'):
    with open('poem_urls.csv', 'r') as f:
        data = f.read()
        urls = [row.split(',')[0] for row in data.split('\n')]
        urls = urls[1:]
        print(len(urls))
        print(len(set(urls)))

        url_category = {}
        rows = data.split('\n')[1:]
        for row in rows:
            url, category = row.split(',')
            url_category.setdefault(url, []).append(category)
        with open('poem_urls_combined.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            for url, categories in url_category.items():
                writer.writerow([url, categories])


def is_valid(driver):
    return not (driver.find_elements(By.CSS_SELECTOR, "h1.notop") or driver.find_elements(By.CSS_SELECTOR, "h2.error"))


def get_titles(driver, url, base_url):
    title_url = url.replace(base_url, '/')
    href = f"[href=\"{title_url}\"]"

    if driver.find_elements(By.CSS_SELECTOR, "a.nocolor.fn"):
        titles = driver.find_elements(By.CSS_SELECTOR, "a.nocolor.fn")

    if driver.find_elements(By.CSS_SELECTOR, href):
        titles += driver.find_elements(By.CSS_SELECTOR, href)
        titles = list(set([title.text for title in titles if title.text != ""]))
        if len(titles) > 0:
            return titles[0]

    return ""


def get_poem(driver, url):
    if driver.find_element(By.CSS_SELECTOR, "div[class^='orig_']"):
        poem = driver.find_element(By.CSS_SELECTOR, "div[class^='orig_']")
        return poem.text
    return ""


def get_poem_categories(driver, url, target_categories):
    if driver.find_elements(By.CSS_SELECTOR, "span.nocolor.cats_dot"):
        span_tag = driver.find_element(By.CSS_SELECTOR, "span.nocolor.cats_dot")
        categories = span_tag.find_elements(By.TAG_NAME, "a")
        categories = set([category.text.lower() for category in categories])
        return list(categories.intersection(target_categories))
    return []


def find_missing_urls():
    with open('poem_urls_combined.csv', 'r') as f:
        data = f.read()
        initial_urls = set([row.split(',')[0] for row in data.split('\n')])

    with open('data.csv', 'r', encoding="utf-8") as f:
        data = f.read()
        reg_pattern = r"https://.*?(?=,)"
        final_urls = set(re.findall(reg_pattern, data))

    missing = initial_urls.difference(final_urls) # To find those URLS present in poem_urls_combined.csv but not in data.csv
    missing.discard('')
    return missing

if __name__ == "__main__":
    if not os.path.exists('data.csv'):
        with open('data.csv', 'w', newline='', encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["url", "title", "poem", "categories"])
        csv_file.close()

    with open("poem_urls.csv", 'r') as f:
        data = f.read()
        rows = data.split('\n')
        urls = [row.split(',')[0] for row in rows]
        # Use below definition to reiterate over missing urls. Uncomment after the code above has been run first.
        # urls = find_missing_urls()

        driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        base_url = "https://allpoetry.com/"
        navigate_to(driver, base_url)
        target_categories = get_target_categories(driver)

        login_url = base_url + "/login"
        navigate_to(driver, login_url)
        username = input("Enter your username: ")
        password = getpass.getpass("Enter your password: ")
        perform_login(driver, username, password)
        time.sleep(1)

        for url in urls:
            time.sleep(5)  # To reduce the load on the website server
            try:
                navigate_to(driver, url)
            except TimeoutException:
                poem_title, poem_text, poem_categories = "", "", ""

            if is_valid(driver):
                poem_title = get_titles(driver, url, base_url)
                poem_text = get_poem(driver, url)
                poem_categories = get_poem_categories(driver, url, target_categories)
                
                with open('data.csv', 'a', newline='', encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow([url, poem_title, poem_text, poem_categories])
                csv_file.close()
        driver.close()
