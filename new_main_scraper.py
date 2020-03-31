from secrets import login_credentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, List
import pandas as pd
import csv
import os
from time import sleep
from random import randint


def read_excel() -> List:
    """
    Read in the excel data as a list of LinkedIn URLs.
    """
    df = pd.read_excel(r'/Users/mduong/PycharmProjects/linkedin_scraper/ventures_linkedin_urls.xlsx')
    lst_links = df['linked_url']
    return lst_links


def limit_list() -> List:
    """
    Limit the number of elements in the list, to test the web scraping mechanism
    on a small subset of the original list of LinkedIn URLs.
    """
    original_lst = read_excel()
    new_lst = original_lst[:]
    return new_lst


def write_csv(data_dict: Dict) -> None:
    """
    Write e dictionary into a CSV file, or update the file if the file already exists.
    :param data_dict: A single dictionary with the LinkedIn extracted data.
    """
    file_name = "scraped_ventures.csv"
    if not os.path.isfile(file_name):
        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['LinkedIn URL','Name', 'Overview', 'Website', 'Industry', 'Financial Services', 'Company size',
                          'Headquarters', 'Type', 'Founded', 'Specialties', 'Phone']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data_dict)
    else:
        with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['LinkedIn URL', 'Name', 'Overview', 'Website', 'Industry', 'Financial Services', 'Company size',
                        'Headquarters', 'Type', 'Founded', 'Specialties', 'Phone']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(data_dict)


def login() -> None:
    """
    Open the browser to the LinkedIn Login page, and login.
    """
    login_dict = login_credentials()
    url = "https://www.linkedin.com/login" # Hardcoded to get the same Login page each time.
    browser = webdriver.Chrome()
    browser.get(url)
    timeout = 20

    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "login__form")))
        browser.find_element_by_id('username').send_keys(login_dict['user'])
        browser.find_element_by_id('password').send_keys(login_dict['pass'])
        browser.find_element_by_xpath("//button[@type='submit']").submit()
    except TimeoutException:
        print("No login form element.")
        try:
            WebDriverWait(browser, timeout).until(EC.visibility_of_element_located(
                (By.CLASS_NAME, "flip-card")))
            browser.find_element_by_link_text('Sign in').click()
            browser.find_element_by_id('login-email').send_keys(login_dict['user'])
            browser.find_element_by_id('login-password').send_keys(login_dict['pass'])
            browser.find_element_by_id('login-submit').click()
        except TimeoutException:
            print("No flip card element on this page.")
            try:
                WebDriverWait(browser, timeout).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "join-form")))
                browser.find_element_by_xpath('//a[@class="form-toggle"]').click()
                browser.find_element_by_id('join-firstname').send_keys(login_dict['user'])
                browser.find_element_by_id('join-lastname').send_keys(login_dict['pass'])
                browser.find_element_by_id('join-email').click()
            except TimeoutException:
                print("No join form element on this page.")
                try:
                    WebDriverWait(browser, timeout).until(
                        EC.visibility_of_element_located((By.ID, "captcha-internal")))
                    browser.quit()
                    login()
                except TimeoutException:
                    print("No captcha here.")
                    get_about_page(browser)
    else:
        try:
            WebDriverWait(browser, 100).until(EC.visibility_of_element_located((By.ID,
                                            "voyager-feed")))
            get_about_page(browser)
        except TimeoutException:
            print("Not logged into the dashboard yet.")


def get_about_page(driver) -> None:
    """
    Get to each company's About page in LinkedIn,
    extract the relevant data, and place it in a dictionary.
    :param driver: The WebDriver object that is currently in session.
    """
    lst_links = limit_list()
    count = 0
    for link in lst_links:
        if not isinstance(link, float): # Dealing with nan values (type: float)
            sleep(randint(15, 35))
            count += 1
            if count % 20 == 0:
                sleep(randint(15, 65))
            driver.get(link)

            data_dict0 = {'LinkedIn URL': link}

            # Extract Overview data, and add it to a dictionary
            data_dict1 = scrape_overview(driver)

            # Extract company stats data
            data_dict2 = scrape_stats(driver)

            # Combine the dictionaries
            data_dict = {**data_dict0, **data_dict1, **data_dict2}
        else:
            # give dictionary with empty string values
            print('link is nan.')
            lst_all_keys = ['LinkedIn URL', 'Name', 'Overview', 'Website', 'Phone', 'Industry', 'Company size',
                         'Headquarters', 'Type', 'Founded', 'Specialties']
            data_dict = dict()
            for key in lst_all_keys:
                if key == 'LinkedIn URL':
                    data_dict[key] = link
                else:
                    data_dict[key] = ''
        write_csv(data_dict)
        # print(data_dict)


# Issue: Need LinkedIn account to have no messages. Else, pop-up message situation. CSS selector clash
def scrape_overview(driver) -> Dict:
    """
    Extract the company's overview, and return the data in a dictionary.
    :param driver: WebDriver object.
    """
    data_dict = dict()
    data_dict['Name'] = ''
    data_dict['Overview'] = ''
    timeout = 20
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "h4.t-18.t-black.t-normal.mb2"))) # Looking for 'Overview' ; previously: t-18 t-black t-normal mb2
    except TimeoutException:
        print("Not on the company page.")
        try:
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR,
                 "div.initial-load-animation.fade-load")))
            return data_dict
        except TimeoutException:
            print("LinkedIn issue - unable to see company page.")
    else:
        try:
            company_overview = driver.find_element_by_css_selector(
                "p.break-words.white-space-pre-wrap.mb5.t-14.t-black--light.t-normal").text
        except NoSuchElementException:
            print("No company overview paragraph element found.")
            company_overview = ''
        try:
            company_name = driver.find_element_by_xpath('//span[@dir="ltr"]').text
        except NoSuchElementException:
            print("Company name element was not found.")
            company_name = ''

        data_dict['Name'] = company_name
        data_dict['Overview'] = company_overview
    return data_dict


def scrape_stats(driver) -> Dict:
    """
    Scrape the company stats data.
    :param driver: A WebDriver object.
    """
    data_dict = dict()
    try:
        keys = driver.find_elements_by_css_selector("dt.org-page-details__definition-term.t-14.t-black.t-bold")
        vals = driver.find_elements_by_css_selector("dd.org-page-details__definition-text.t-14.t-black--light.t-normal")
        comp_size = driver.find_element_by_css_selector("dd.org-about-company-module__company-size-definition-text."
                                                        "t-14.t-black--light.mb1.fl")
        if len(keys) != len(vals):
            if " on LinkedIn" in vals:
                for value in vals:
                    vals.remove(value)
        if "employees" in vals:
            for value in vals:
                vals.remove(value)

        for key in keys:
            if key.text == 'Company size':
                keys.remove(key)

        for key, val in zip(keys, vals):
            if 'Phone number is' in val.text:
                data_dict[key.text] = val.text.split('P', 1)[0].strip()
            elif not isinstance(val, str):
                data_dict[key.text] = val.text
            else:
                data_dict[key.text] = val
        data_dict['Company size'] = comp_size.text.split('-', 1)[0]
    except NoSuchElementException:
        print("No d1 overflow-hidden element found.")
    return data_dict


if __name__ == '__main__':
    login()

