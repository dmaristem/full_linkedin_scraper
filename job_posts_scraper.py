from secrets import login_credentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from typing import Dict, List
import csv
import os
from time import sleep
from random import randint
from bs4 import BeautifulSoup

# Find job posts on LinkedIn for companies in the GTA that have the keyword 'ergonomic' in the job descriptions.
# Scrape these job descriptions, and then filter them based on the existence of keywords
# Steps:
    # 1. Login
    # 2. Go to this link: https://www.linkedin.com/jobs/search/
    # 3. Put 'Greater Toronto Area Metropolitan Area' into location search > Search (find input bar, type, press search button)
    # 4. Scrape Job postings from page 1 to the last page

def write_csv(data_dict: Dict) -> None:
    """
    Write e dictionary into a CSV file, or update the file if the file already exists.
    :param data_dict: A single dictionary with the LinkedIn extracted data.
    """
    file_name = "scraped_job_posts.csv"
    if not os.path.isfile(file_name):
        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Job Title', 'Company', 'Location', 'Job Description', 'Seniority Level', 'Employment Type',
                          'Job Functions', 'Industry', 'Number of Applicants', 'Number of Employees']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data_dict)
    else:
        with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Job Title', 'Company', 'Location', 'Job Description', 'Seniority Level', 'Employment Type',
                          'Job Functions', 'Industry', 'Number of Applicants', 'Number of Employees']
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
                    # get_job_page(browser)
                    get_job_ids(browser)
    else:
        try:
            WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.ID,
                                            "voyager-feed")))
            # get_job_page(browser)
            get_job_ids(browser)
        except TimeoutException:
            print("Not logged into the dashboard yet.")


def get_job_ids(driver) -> None:
    """
    Go to job search page and get all the job ids, which
    can be replaced into the url to get unique links.
    :param driver: The WebDriver object that is currently in session.
    :return: None.

    Example ID: 1805650202
    LinkedIn URL: https://www.linkedin.com/jobs/search/?currentJobId=1805650202
    """
    # 25 job postings on a job search page
    # <div data-job-id="urn:li:fs_normalized_jobPosting:1805650202"></div>
    driver.get('https://www.linkedin.com/jobs/search/?geoId=90009551&location=Greater%20Toronto%20Area%20Metropolitan%20Area&start=150')
    try:
        # WebDriverWait(driver, 15).until(EC.visibility_of_element_located(
        # (By.CSS_SELECTOR, "div.data-control-id")))
        # WebDriverWait(driver, 15).until(EC.visibility_of_element_located(By.XPATH("//*[@data-control-id]")))
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located(By.XPATH("//div[contains(@data-job-id, "
                                                                                  "'urn:li:fs_normalized_jobPosting:1757159406')]")))
        # div class: neptune-grid one-column full-height
    except TimeoutException:
        print('No element with data-control-id found.')
    except TypeError:
        print(type(driver))
    # html = BeautifulSoup(driver.page_source, 'html.parser')
    # lst = html.find_all('div', {'data-control-id': True})
    # print(len(lst))
    lst = []
    try:
        div = driver.find_elements_by_class_selector("div.data-control-id")
        lst.append(div)
    except NoSuchElementException:
        print('No div element found with data-control-id selector.')
    except AttributeError:
        elem = driver.find_elements_by_xpath("//div[contains(@data-job-id)]")
        print(elem.get_attribute("value"))

    lst_ids = []
    for elem in lst:
        lst_ids.append(elem.content)
    print(lst_ids)


def get_job_page(driver) -> None:
    """
    Go to the job search page.
    :param driver: The WebDriver object that is currently in session.
    """
    # driver.get('https://www.linkedin.com/jobs/search/')
    # Use link that goes to job search with GTA location specification
    driver.get('https://www.linkedin.com/jobs/search/?geoId=90009551&location=Greater%20Toronto%20Area%20Metropolitan%20Area&start=150')

    # Find the job search bar id and type in : Greater Toronto Area Metropolitan Area
    # try:
    #     driver.find_element_by_class_name('jobs-search-box__text-input')
    # except NoSuchElementException:
    #     print('no job search bar element')
    # return None

    # to get job title and company: target div class : jobs-details-top-card__content-container
    # to get job description: article class : jobs-description__container  m4


    # Get all <a data-control-id> href links (goes to job descriptions)
    # driver.find_element_by_tag_name('a data-control-id')
    html = BeautifulSoup(driver.page_source, 'html.parser')  # works with 'html.parser' too.
    # print(soup)
    # h3 class 'job-card-search__title artdeco-entity-lockup__title ember-view
    # a tag is found right underneath h3 class

    # lst_tags = html.find_all('h3', {'class':'job-card-search__title'})
    lst = html.find_all('ul', {'class': 'jobs-search-results__list artdeco-list'})
    lst_a_tags = driver.find_elements_by_tag_name('li')   # empty lst
    # lst_a_tags = lst.find_all('a', {'class': 'job-card-search__link-wrapper.ember-view'})
    print(lst_a_tags)
    # return
    for item in lst:
        # tag = item.find('a', {'data-control-id': True})
        # print(tag.text)
        print(item.text)
    # print(lst)
    # print(lst_tags)
        # find_next_sibling('div').find_all('a')

    # a_tags = html.find_all('a', {'data-control-id': True})
    # a_tags = html.find_all('div', {'data-job-id': True})
    # print(a_tags)
    # print(len(a_tags))

    return

    # a_tags = driver.find_elements_by_xpath('//a[@data-control-id]')
    # links = driver.find_elements_by_partial_link_text('/jobs/')
    # print(len(a_tags))
    # print(len(links))

    lst_links = []
    for tag in a_tags:
        if tag is not None:
            try:
                link = tag.get_attribute('href').text
                lst_links.append(link)
            except StaleElementReferenceException:
                # print(tag.get_attribute('innerHTML'))
                pass
            except TypeError:
                # print(tag)
                pass
        # link = tag.find_element_by_css_selector('a.href').text
    print(lst_links)
    return




 # --------------
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

# experience-section

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
    lst_data = []
    try:
        stats = driver.find_elements_by_class_name("overflow-hidden")
        # for stat in stats: # seems that stat is every text in stats, existing as one single long string.
        #     lst_data = stat.text.split('\n') # that's why I need to split the long string up
        # lst_data = clean_stats_lst(lst_data)
        # print(lst_data)
        # for stat in stats:
        keys = driver.find_elements_by_css_selector("dt.org-page-details__definition-term.t-14.t-black.t-bold")
        vals = driver.find_elements_by_css_selector("dd.org-page-details__definition-text.t-14.t-black--light.t-normal")
        comp_size = driver.find_element_by_css_selector("dd.org-about-company-module__company-size-definition-text."
                                                        "t-14.t-black--light.mb1.fl")
        # print(comp_size)

        if len(keys) != len(vals):
            if " on LinkedIn" in vals:
                for value in vals:
                    vals.remove(value)
        if "employees" in vals:
            for value in vals:
                vals.remove(value)

                    # print(value)

        # vals.insert(2, comp_size)
        for key in keys:
            if key.text == 'Company size':
                keys.remove(key)

        for key, val in zip(keys, vals):
            # print(key.text, val.text)
            # print(val.text)
            if 'Phone number is' in val.text:
                data_dict[key.text] = val.text.split('P', 1)[0].strip()
            elif not isinstance(val, str):
                data_dict[key.text] = val.text
            else:
                data_dict[key.text] = val

        data_dict['Company size'] = comp_size.text.split('-', 1)[0]


        print(data_dict)
    except NoSuchElementException:
        print("No d1 overflow-hidden element found.")
    # return make_stats_dict(lst_data)
    return data_dict




if __name__ == '__main__':
    login()

