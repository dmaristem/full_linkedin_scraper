# full_linkedin_scraper
A Python web-scraper for LinkedIn company, person, and job-level data. 

For the company scraper:
- name
- description/overview
- website
- phone
- headquarters
- founding date
- industry type
- speciaities 

## Dependencies 
- Selenium WebDriver
- pandas 

## Installations
Download the appropriate WebDriver version for your browser of choice.
Ensure that the chromedriver.exe file is in your project folder. 

This project used [WebDriver for Chrome](http://chromedriver.chromium.org/downloads)
(Chrome Version 74 and ChromeDriver 74). 

To check your Chrome version:
1. Go to the upper right corner of your browser and click the 'three vertical dots' icon.
2. Select 'Settings' from the drop-down menu. 
3. Once on the Settings page, go to the upper left corner and click the 'three horizontal bars' icon. 
4. Select 'About Chrome'. 

## Usage
**main_scraper.py** is the file to run. 
- Edit the path to the file you want to read the data in from --> read_excel function
- Edit the name of the file you want to save your data output in --> write_csv function
- Edit the amount of LinkedIn URLs you want to go through --> limit_list function
