import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from mailjet_rest import Client

def sendSms(smsServer,smsToken,smsFrom,smsTo,smsMessage):
    requestUrl=f'https://{smsServer}/sms.do?from={smsFrom}&to{smsTo}&message={smsMessage}&json=True'
    requestHeader = {"Authorization": f"Bearer {smsToken}"}
    print(f'requestUrl: {requestUrl}')
    print(f'requestHeader: {requestHeader}')
    result = requests.get(requestUrl,headers=requestHeader)
    print(result.text)

    return result

url = 'https://www.microsoft.com/en-us/learning/community-blog.aspx'
wantedString = os.environ['SEARCH_STRING']
siteName = 'Born To Learn'

# $ export CHROME_PATH=/usr/bin/chrome
chrome_bin = os.environ['GOOGLE_CHROME_BIN']
#chrome_bin = '/usr/bin/chrome'
print(f'chrome_bin: {chrome_bin}')

# $ export CHROME_DRIVER=~/Python/BtlWebScrapper/venv/chromedriver/chromedriver
# chrome_driver = '/home/user1/Python/BtlWebScrapper/venv/chromedriver/chromedriver'
chrome_driver = os.environ['CHROMEDRIVER_PATH']
print(f'chrome_driver: {chrome_driver}')

chrome_options = Options()
chrome_options.binary_location = chrome_bin
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--headless")

# chrome driver logging
# outputdir='/home/user1'
# service_log_path = "{}/chromedriver.log".format(outputdir)
# service_args = ['--verbose']
# print(f'service_log: {service_log_path}')

driver = webdriver.Chrome(executable_path=chrome_driver,
#                           service_args=service_args,
#                           service_log_path=service_log_path,
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
    items = blogposts.findAll('div', class_="btl-blog-posts-contents-right")

    regex = f'\\b{wantedString}\\b'
    matches = []
    for i in items:
        post = i.getText()
        match = re.search(regex, post, re.IGNORECASE)
        if match:
            matches.append(post)

    if len(matches) > 0:
        message = 'patten matched in: \n'
        for m in matches:
            message += f' --> {m}\n'
    else:
        message = None
else:
    message = 'Couldn\'t retrieve page contents'

print(message)

if message:
    API_KEY = os.environ['MJ_APIKEY_PUBLIC']
    API_SECRET = os.environ['MJ_APIKEY_PRIVATE']

    mailjet = Client(auth=(API_KEY, API_SECRET), version='v3')
    fromname = 'BornToLearn - WebScrapper'
    sender = 'messanger@tutamail.com'
    recipients = [{'Email': 'ignorethismessage@gmail.com'}]
    subject = f'{wantedString} - found on {siteName}!'
    #message = "Today\'s Pact Book: {}\n URL: {}".format(dotd,url)

    css = '''
    <style type="text/css">
    body {font-family: Verdana, Geneva, Arial, Helvetica, sans-serif;}
    h2 {clear: both;font-size: 130%; }
    h3 {clear: both;font-size: 115%;margin-left: 20px;margin-top: 30px;}
    p {margin-left: 20px; font-size: 14px;}
    </style>
    '''

    html_head = '''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">
    <html><head><title>{}</title>
    {}
    </head>
    '''.format(subject,css)

    html_body = '''
    <body>
    <p>Phrase: {0} was found on {3}\n</p>

    <h2>{1}</h2>
    <h3> {2} </h3>
    </body>
    '''.format(wantedString,message,url,siteName)

    html_foot = '</html>'

    message = html_head + html_body + html_foot

    email = {
    	'FromName': fromname,
    	'FromEmail': sender,
    	'Subject': subject,
    	'Html-Part': message,
    	'Recipients': recipients
    }

    response = mailjet.send.create(email)
    print("MailJet response:{}".format(response))

smsServer1 = os.environ['SMS_SERVER1']
smsServer2 = os.environ['SMS_SERVER2']
smsToken = os.environ['SMS_TOKEN']
smsFrom = os.environ['SMS_NUMBER']
smsTo = os.environ['SMS_NUMBER']
smsMessage = f'{wantedString}, found on {siteName}'

result = sendSms(smsServer1,smsToken,smsFrom,smsTo,smsMessage)
if result != '<Response [200]>':
    result = sendSms(smsServer2,smsToken,smsFrom,smsTo,smsMessage)
print(f'SmsAPI response:{result}')
