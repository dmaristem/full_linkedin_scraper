from secrets import login_credentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, List
from parsel import Selector
import pandas as pd
import csv
import os
from time import sleep
from random import randint
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup, Tag, NavigableString


# def read_excel() -> List:
#     """
#     Read in the excel data as a list of LinkedIn URLs.
#     """
#     # data = pd.read_excel(r'C:\Users\Tony Stark\PycharmProjects\linkedin_scraper\2017_LinkedIn_Companies.xlsx')
#     data = pd.read_excel(r'/Users/mduong/PycharmProjects/linkedin_scraper/2017_Extra_LinkedIn_Companies.xlsx')
#     df = pd.DataFrame(data, columns=['LinkedIn Link']) # 2018 column name
#
#     # Get list of links
#     lst_links = [link[0] for link in df.itertuples(
#         index=False)]
#     return lst_links
#
#
# def limit_list() -> List:
#     """
#     Limit the number of elements in the list, to test the web scraping mechanism
#     on a small subset of the original list of LinkedIn URLs.
#     """
#     original_lst = read_excel()
#     new_lst = original_lst[:]
#     return new_lst


def write_csv(data_dict: Dict) -> None:
    """
    Write e dictionary into a CSV file, or update the file if the file already exists.
    :param data_dict: A single dictionary with the LinkedIn extracted data.
    """
    file_name = "linked_persons.csv"
    if not os.path.isfile(file_name):
        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Name', 'Overview', 'Website', 'Industry', 'Financial Services', 'Company size', 'Headquarters', 'Type', 'Founded', 'Specialties', 'Phone']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data_dict)
    else:
        with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Name', 'Overview', 'Website', 'Industry', 'Financial Services', 'Company size', 'Headquarters',
                          'Type', 'Founded', 'Specialties', 'Phone']
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
    get_about_page(browser)
    browser.quit()
    #     try:
    #         WebDriverWait(browser, timeout).until(EC.visibility_of_element_located(
    #             (By.CLASS_NAME, "flip-card")))
    #         browser.find_element_by_link_text('Sign in').click()
    #         browser.find_element_by_id('login-email').send_keys(login_dict['user'])
    #         browser.find_element_by_id('login-password').send_keys(login_dict['pass'])
    #         browser.find_element_by_id('login-submit').click()
    #     except TimeoutException:
    #         print("No flip card element on this page.")
    #         try:
    #             WebDriverWait(browser, timeout).until(
    #                 EC.visibility_of_element_located((By.CLASS_NAME, "join-form")))
    #             browser.find_element_by_xpath('//a[@class="form-toggle"]').click()
    #             browser.find_element_by_id('join-firstname').send_keys(login_dict['user'])
    #             browser.find_element_by_id('join-lastname').send_keys(login_dict['pass'])
    #             browser.find_element_by_id('join-email').click()
    #         except TimeoutException:
    #             print("No join form element on this page.")
    #             try:
    #                 WebDriverWait(browser, timeout).until(
    #                     EC.visibility_of_element_located((By.ID, "captcha-internal")))
    #                 browser.quit()
    #                 login()
    #             except TimeoutException:
    #                 print("No captcha here.")
    #                 get_about_page(browser)
    # else:
    #     try:
    #         WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.ID,
    #                                         "voyager-feed")))
    #         get_about_page(browser)
    #     except TimeoutException:
    #         print("Not logged into the dashboard yet.")


def get_about_page(driver) -> None:
    """
    Get to each person's About page in LinkedIn,
    extract the relevant data, and place it in a dictionary.
    :param driver: The WebDriver object that is currently in session.
    """
    # lst_links = limit_list()
    lst_links = ['https://www.linkedin.com/in/mariannaciocio/',
                 'https://www.linkedin.com/in/hera-koliatsos-6a8684a1/',
                 'https://www.linkedin.com/in/tojason/', # One hierarchical item under Experience
                 'https://www.linkedin.com/in/mer-harhar-4765a5194/' # No About, one item under Experience
                 ]
    # 'https://www.linkedin.com/in/fabio-cavaggioni-a47ba82/'
    count = 0
    for link in lst_links:
        if not isinstance(link, float): # Dealing with nan values (type: float)
            sleep(randint(15, 35))
            count += 1
            if count % 20 == 0:
                sleep(randint(15, 65))
            driver.get(link)

            # Extract Overview data, and add it to a dictionary
            data_dict1 = scrape_overview(driver)
            print(data_dict1)

            # Extract company stats data
            # data_dict2 = scrape_stats(driver)

            # Combine the dictionaries
            # data_dict = {**data_dict1, **data_dict2}
        # else:
        #     # give dictionary with empty string values
        #     print('link is nan.')
        #     lst_all_keys = ['Name', 'Overview', 'Website', 'Phone', 'Industry', 'Company size',
        #     'Headquarters', 'Type', 'Founded', 'Specialties']
        #     data_dict = dict()
        #     for key in lst_all_keys:
        #         data_dict[key] = ''
        # write_csv(data_dict)
        # print(data_dict)

# Issue: Need LinkedIn account to have no messages. Else, pop-up message situation. CSS selector clash
def scrape_overview(driver) -> Dict:
    """
    Extract the Person's profile overview, and return the data in a dictionary.
    :param driver: WebDriver object.
    """
    data_dict = dict()
    data_dict['Name'] = ''
    data_dict['Location'] = ''
    timeout = 20
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "core-rail"))) # Looking for class name 'core-rail'
        # which is associated with the person's header box
        print("On Person's Profile Page!")
    except TimeoutException:
        print("Not on the person's LinkedIn profile page.")
        try:
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR,
                 "div.initial-load-animation.fade-load")))
            return data_dict
        except TimeoutException:
            print("LinkedIn issue - unable to see profile page.")
    else:
        # only one occurrence of the chosen css selectors (more general strategy would be better long-term though)
        # page_source = driver.page_source
        # html = BeautifulSoup(page_source, 'html.parser')
        # print(html)
        # return
        # sel = Selector(text=driver.page_source)
        # about = sel.xpath('//*[@class="artdeco-container-card pv-profile-section pv-about-section ember-view"]/text()')

        soup_level = BeautifulSoup(driver.page_source, 'html.parser')
        # print(soup_level)
        # print(type(soup_level))
        # text=soup_level.get_text()
        # text = soup_level.find("section", class_="artdeco-container-card pv-profile-section pv-about-section ember-view")
        # for elem in text:
            # print(elem)

        # text2 = soup_level.find("p", class_="pv-about__summary-text mt4 t-14 ember-view").extract()
        # print(text2)
        try:
            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                            "p.pv-about__summary-text.mt4.t-14.ember-view")))
            try:
                text2 = soup_level.find("p", class_="pv-about__summary-text mt4 t-14 ember-view").extract()
                print(text2)
                print(text2.get_text())
            except AttributeError:
                text2 = ''
        except TimeoutException:
            print("TimeOutException waiting for About paragraph section element to be located.")
        # text2 = soup_level.find("p", class_="pv-about__summary-text mt4 t-14 ember-view").get_text() # AttributeError: 'NoneType' object has no attribute 'get_text'
        # print(type(text2)) # class NoneType, class bs4.element.Tag
        # print(text2)
        # for elem in text2:
        #     print(elem.get_text())
        # print(text2)


        # about = soup_level.xpath('//*[@class="artdeco-container-card pv-profile-section pv-about-section ember-view"]/text()')
        # about = soup_level.xpath('//*[@id="bpr-guid-1707093"]')
        # print(about)
        return

        try:
            name = driver.find_element_by_css_selector("li.break-words").text
        except NoSuchElementException:
            print("Name element was not found.")
            name = ''
        try:
            byline = driver.find_element_by_css_selector(
                "h2.mt1.t-18.t-black.t-normal").text
        except NoSuchElementException:
            print("Byline element was not found.")
            byline = ''
        try:
            location = driver.find_element_by_css_selector(
                "li.t-16.t-black.t-normal.inline-block").text
        except NoSuchElementException:
            print("Location element was not found.")
            location = ''
        try:
            connections = driver.find_element_by_css_selector(
                "span.t-16.t-black.t-normal").text
        except NoSuchElementException:
            print("Connections element was not found.")
            connections = ''
        # try:
        #     # xpath to extract the text from the class containing the college
        #     college = driver.find_element_by_xpath('//*[starts-with(@class,'
        #         '"pv-about__summary-text mt4 t-14 ember-view")]').text
        # except NoSuchElementException:
        #     college = ''

        # try:
        #     # WebElement is returned here and it's not iterable - because using find_element_by_xpath, not find_elements_by_xpath
        #     # Occasionally works too! Works for Marianna, but not for Jason Tod
        #     about= driver.find_element_by_xpath('//div[contains(@class, "pv-oc") and contains(@class, "ember-view")]').text
        #     # about = driver.find_elements_by_xpath('//span[contains(@class, "lt-line-clamp__line")]')
        #     # about = ''
        #     # for element in elements:
        #     #     print(element.text)
        #
        #         # about += element.text
        #     # print(type(about)) # string
        #     # print(about) # empty string ''     ... so it is the text attribute that is having issues?
        #     # get_attribute('textContent') not working
        #
        #     # The print statement runs, so about = driver ... is run ... but the text is not captured
        #     print('about element was found!')
        #     # about = ''
        #     # for element in about0:
        #     #     about += element.text
        # except NoSuchElementException:
        #     print('pls god why no about')
        #     about = ''
        # try:
        #     WebDriverWait(driver, timeout).until(
        #         lambda s: s.find_element_by_css_selector('section.artdeco-container-card.pv-profile-section.pv-about-section.ember-view').is_displayed())
        #     try:
        #         about = driver.find_element_by_css_selector('section.artdeco-container-card.pv-profile-section.pv-about-section.ember-view').text
        #     except NoSuchElementException:
        #        print('No About text!')
        #        about = ''
        #     # TimeOutException - add a check for that
        # except TimeoutException:
        #     print('About element not found!')
        #     about = ''

        # try:
        #     WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "profile-detail")))
        #     try:
        #         WebDriverWait(driver, timeout).until(lambda s: s.find_element_by_css_selector('section.pv-about-section').is_displayed())
        #         about = driver.find_element_by_css_selector('section.pv-about-section').text
        #         # about = driver.find_element_by_css_selector(
        #         #     "section.artdeco-container-card.pv-profile-section.pv-about-section.ember-view").get_attribute(
        #         #     'innerHTML')
        #         # about = driver.find_element_by_css_selector(
        #         #     "section.artdeco-container-card.pv-profile-section.pv-about-section.ember-view").text
        #         # about = driver.find_element_by_css_selector('p.pv-about__summary-text.mt4.t-14.ember-view').text
        #         # lines = driver.find_elements_by_css_selector('lt-line-clamp__line')
        #         # print(type(lines))
        #         # about = ''
        #         # print('Clamp line found')
        #         # if lines is None:
        #         #     print('empty list')
        #         # else:
        #         #     print('list is not empty')
        #         #     for line in lines:
        #         #         # print(type(line))
        #         #         about += line.text
        #                 # print(line.text)
        #
        #     except NoSuchElementException:
        #         print('About element not found.')
        #         about = ''
        # except TimeoutException:
        #     print('Timeout waiting for profile-detail.')
        #     about = ''
            # WebDriverWait(driver, timeout).until(
            #     EC.visibility_of_element_located((By.CSS_SELECTOR, "section.artdeco-container-card.pv-profile-section.pv-about-section.ember-view")))
            # about = driver.find_element_by_css_selector("section.artdeco-container-card.pv-profile-section.pv-about-section.ember-view").get_attribute('innerHTML')
            # about = innerHTML.text
        # except NoSuchElementException:
        #     print("About element not found.")
        #     about = ''
        # try:
        #     WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "pv-about__summary-text.mt4.t-14.ember-view")))
        #     try:
        #         # Check for the existence of the About heading
        #         # driver.find_element_by_xpath('/h2[text()="About"]') # Not working. Find out why later.
        #         about = driver.find_element_by_css_selector(
        #             "p.pv-about__summary-text.mt4.t-14.ember-view").text  # Sometimes works.
        #         # about = driver.find_element_by_xpath("//h2[contains(text() , 'About')]/following-sibling::span").text
        #         # about = driver.find_element_by_xpath("//h2[contains(text() , 'About')]")
        #         # about = driver.find_elements_by_xpath("//h2[@class='pv-profile-section__card-heading]")[0].text
        #         # about = driver.find_element_by_xpath("//h2[@class='pv-profile-section__card-heading]").text
        #         # about = driver.find_element_by_xpath("//p[@class='pv-about__summary-text mt4 t-14 ember-view").text # Should work now due to no dots
        #     except NoSuchElementException:
        #         print("About element element was not found.")
        #         about = ''
        # except TimeoutException:
        #     print("Maybe the About element hasn't been loaded yet. Nothing found.")
        #     about = ''
        try:
            WebDriverWait(driver, timeout).until(lambda s: s.find_element_by_id('experience-section').is_displayed())
            try:
                experience = driver.find_element_by_id('experience-section').text
            # experience = driver.find_element_by_css_selector\
            #     ("ul.pv-profile-section__section-info.section-info").text
            except NoSuchElementException:
                print('No Experience text!')
                experience = ''
        except TimeoutException:
            print("Experience element was not found.")
            experience = ''
        try:
            WebDriverWait(driver, timeout).until(lambda s: s.find_element_by_id('education-section').is_displayed())
            try:
                education = driver.find_element_by_id('education-section').text
            except NoSuchElementException:
                print('No Education text!')
                education = ''
        except TimeoutException:
            print("Education element was not found.")
            education = ''
        # try:
        #     WebDriverWait(driver, timeout).until(lambda s: s.find_element_by_css_selector('pv-about__summary-text').is_displayed())
        #     try:
        #         about = driver.find_element_by_css_selector('pv-about__summary-text').text
        #     except NoSuchElementException:
        #         print('No Abouttext!')
        #         about = ''
        # except TimeoutException:
        #     print("About element was not found.")
        #     about = ''


        # current_url = driver.current_url
        # page_source = driver.page_source
        # # response = simple_get(current_url)
        # # print(current_url)
        # html = BeautifulSoup(page_source, 'html.parse')
        # if response is not None:
        #     html = BeautifulSoup(response, 'html.parser')
        #     about = html.find('section', attrs={'class': 'pv-about-section'})
        #     print(about)
        #     print(type(about))
        # else:
        #     about = ''


        data_dict['Name'] = name
        data_dict['Byline'] = byline
        data_dict['Location'] = location
        data_dict['Connections'] = connections
        data_dict['About'] = about
        data_dict['Experience'] = experience
        data_dict['Education'] = education
        # data_dict['Skills'] = skills
    return data_dict


def scrape_stats(driver) -> None:
    """
    Scrape the company stats data.
    :param driver: A WebDriver object.
    """
    lst_data = []
    try:
        # stats = driver.find_elements_by_class_name("overflow-hidden")
        experience = driver.find_element_by_id("experience-section")
        experience = experience.find_elements_by_class("pv-entity__position-group-pager pv-profile-section__list-item ember-view")
        for exp in experience:
            print(exp.text)

    #     for stat in stats: # seems that stat is every text in stats, existing as one single long string.
    #         lst_data = stat.text.split('\n') # that's why I need to split the long string up
    #     lst_data = clean_stats_lst(lst_data)
    #
    except NoSuchElementException:
        print("No d1 overflow-hidden element found.")
    # return make_stats_dict(lst_data)


def clean_stats_lst(lst_data: list) -> List:
    """ Clean the list of company stats.
    lst_data: The list of company stats.
    """
    for elem in lst_data:
        if 'Phone number is' in elem:
            lst_data.remove(elem)
    return lst_data


def make_stats_dict(lst_data: list) -> Dict:
    """
    Create a dictionary out of the list of company stats.
    If the dictionary is missing keys from the list of all keys,
    then add them in.
    :param lst_data: The cleaned list of company stats.
    """
    # Make the dictionary
    data_dict = {}
    lst_all_keys = ['Website', 'Phone', 'Industry', 'Company size', 'Headquarters', 'Type', 'Founded', 'Specialties']

    for i in range(len(lst_data)):
        if i % 2 == 0 and lst_data[i] != '':
            data_dict[lst_data[i]] = ''
        elif i % 2 != 0:
            data_dict[lst_data[i - 1]] = lst_data[i]

    # Add in any missing keys
    for key in lst_all_keys:
        if data_dict.get(key) is None:
            data_dict[key] = ''

    return data_dict

# BEAUTIFUL SOUP FUNCTIONS
# Download web pages to get the raw HTML, with the help of the requests package
def simple_get(url: str):
    """
    Attempts to get the content at 'url' by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the text content, otherwise return None.
    """
    try:
        # The closing() function ensures that any network resources are freed when they go out of scope in the with block.
        # Using closing() is a good practice to help prevent fatal errors and network timeouts
        with closing(get(url, stream=True, verify=False)) as resp:
            if is_good_response(resp):
                print("HTTP Error: {0}".format(resp.raise_for_status()))
                print(resp.headers)
                # the content is the HTML document
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp) -> bool:
    """
     Return True if the response seems to be HTML, otherwise return False.
    """
    content_type = resp.headers['Content-Type'].lower()
    print("HTTP Status Code: {0}".format(resp.status_code))
    return (resp.status_code == 200 and content_type is not None and content_type.find('html') > -1)

def log_error(e):
    """
    This function prints the errors.
    """
    print(e)


if __name__ == '__main__':
    login()

