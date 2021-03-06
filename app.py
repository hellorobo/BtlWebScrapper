import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from mailjet_rest import Client
import pymongo
from datetime import datetime

def sendSms(smsServer,smsToken,smsFrom,smsTo,smsMessage):
    requestUrl = f'https://{smsServer}/sms.do?from={smsFrom}&to={smsTo}&message={smsMessage}&format=json'
    requestHeader = {"Authorization": f"Bearer {smsToken}"}
    result = requests.get(requestUrl,headers=requestHeader)
    print(f'SmsAPI:{result}')

    return result

url = 'https://www.microsoft.com/en-us/learning/community-blog.aspx'
wantedString = os.environ['SEARCH_STRING']
siteName = 'Born To Learn'

dbserver = os.environ['DB_SERVER']
dbname = os.environ['DB_NAME']
dbcollection = os.environ['DB_COLLECTION']
dbuser = os.environ['DB_USER']
dbpass = os.environ['DB_PASS']

connection = pymongo.MongoClient('mongodb://{}:{}@{}/{}'.format(dbuser,dbpass,dbserver,dbname))
db = connection[dbname]
posts_col = db[dbcollection]
logs_col = db.logs

# $ export CHROME_PATH=/usr/bin/chrome
chrome_bin = os.environ['GOOGLE_CHROME_BIN']
#chrome_bin = '/usr/bin/chrome'
#print(f'chrome_bin: {chrome_bin}')

# $ export CHROME_DRIVER=~/Python/BtlWebScrapper/venv/chromedriver/chromedriver
# chrome_driver = '/home/user1/Python/BtlWebScrapper/venv/chromedriver/chromedriver'
chrome_driver = os.environ['CHROMEDRIVER_PATH']
#print(f'chrome_driver: {chrome_driver}')

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
isPageLoaded = False
try:
    element_present = EC.presence_of_element_located((By.ID, neededElement))
    WebDriverWait(driver, timeout).until(element_present)
    isPageLoaded = True
    print("Web page loaded completely")
except TimeoutException:
    print ("Timed out waiting for page to load")
except ConnectionResetErorr:
    print ("Connection reset by peer")
    
if isPageLoaded:
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, 'lxml')

    blogposts = soup.find('ul', id="btl-blog-posts-ul")
    items = blogposts.findAll('div', class_="btl-blog-posts-contents-right")
    
    isMatched = False
    regex = f'\\b{wantedString}\\b'
    matches = []
    for i in items:
        post = i.getText()
        match = re.search(regex, post, re.IGNORECASE)
        if match:
            query = {'post': post}
            try:
                existingDocument = posts_col.find_one_and_replace(
                                filter=query,
                                replacement=query,
                                upsert=True,
                                return_document=pymongo.ReturnDocument.BEFORE
                                )
                if existingDocument == None:
                    matches.append(post)

            except Exception as e: print("Exception: ", type(e), e)
    if len(matches) > 0:
        isMatched = True
        message = 'patten matched in: \n'
        for m in matches:
            message += f' --> {m}\n'
    else:
        message = None
else:
    message = 'Couldn\'t retrieve page contents'

print(message)

try:
    r = requests.get('https://www.icanhazip.com/')
    ip = r.text
    now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    result = logs_col.insert_one(
                {"datetime": now,
                 "ip": ip,
                 }
                )
    print('{} connection made from {}'.format(now, ip))
except Exception as e: print("Exception: ", type(e), e)

connection.close()

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
    
    if isMatched:
        smsServer1 = os.environ['SMS_SERVER1']
        smsServer2 = os.environ['SMS_SERVER2']
        smsToken = os.environ['SMS_TOKEN']
        smsFrom = os.environ['SMS_FROM']
        smsTo = os.environ['SMS_TO']
        smsMessage = f'ALERT! Heroku/btl-webscrapper found \'{wantedString}\' on {url}'

        result = sendSms(smsServer1,smsToken,smsFrom,smsTo,smsMessage)
        if result.status_code != 200:
            result = sendSms(smsServer2,smsToken,smsFrom,smsTo,smsMessage)
        print(f'SmsAPI:{result.text}')
