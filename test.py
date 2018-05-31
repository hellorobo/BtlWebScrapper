import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

#a1 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#a2 = ' (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
#agent = {'User-Agent': a1 + a2}

url = 'https://www.microsoft.com/en-us/learning/community-blog.aspx'

# $ export CHROME_PATH=/usr/bin/chrome
##chrome_bin = os.environ['CHROME_PATH']
chrome_bin = '/usr/bin/chrome'
print(f'chrome_bin: {chrome_bin}')

# $ export CHROME_DRIVER=~/Python/BtlWebScrapper/venv/chromedriver/chromedriver
chrome_driver = '/home/user1/Python/BtlWebScrapper/venv/chromedriver/chromedriver'
#chrome_driver = os.environ['CHROME_DRIVER']
print(f'chrome_driver: {chrome_driver}')

# chrome driver logging
outputdir='/home/user1'
service_log_path = "{}/chromedriver.log".format(outputdir)
service_args = ['--verbose']
print(f'service_log: {service_log_path}')

chrome_options = Options()
chrome_options.binary_location = chrome_bin
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(executable_path=chrome_driver,
                           service_args=service_args,
                           service_log_path=service_log_path,
                           chrome_options=chrome_options)
driver.get(url)

# wait for needed content to load
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
timeout = 5
neededElement = 'btl-blog-post-1-right'
try:
    element_present = EC.presence_of_element_located((By.ID, neededElement))
    WebDriverWait(driver, timeout).until(element_present)
    isPageLoaded = True
    print("OK, found page element")
except TimeoutException:
    isPageLoaded = False
    print ("Timed out waiting for page to load")

if isPageLoaded:
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, 'lxml')

    blogposts = soup.find('ul', id="btl-blog-posts-ul")
    items = soup.findAll('div', class_="btl-blog-posts-contents-right")
    pattern = '\bExam Study\b'
    matches = []
    for i in items:
        post = i.getText()
        matches.append(re.search(pattern, post, re.IGNORECASE))

    if len(matches) > 0:
        print(f'patten matched in: \"{post}\"')
    else:
        print(f'no match for {pattern}')
    
else:
    message = 'Couldn\'t retrieve page contents'


# TODO: sent email
