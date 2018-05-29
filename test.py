from bs4 import BeautifulSoup
from selenium import webdriver


a1 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
a2 = ' (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
agent = {'User-Agent': a1 + a2}

url = 'https://www.microsoft.com/en-us/learning/community-blog.aspx'


browser = webdriver.PhantomJS()
browser.get(url)
html = browser.page_source
soup = BeautifulSoup(html, 'lxml')
blogposts = soup.find_all('div', class_="btl-blog-posts-contents-right")

