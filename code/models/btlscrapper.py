from datetime import datetime
from bs4 import BeautifulSoup
import requests


class EbookModel():

    a1 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    a2 = ' (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
    agent = {'User-Agent': a1 + a2}

    def __init__(self):
        pass

    def get(self, url):
        self.url = url
        resp = requests.get(self.url, headers=self.agent)
        soup = BeautifulSoup(resp.text, 'html.parser')
        self.title = soup.select('.dotd-title')[0].text.strip()
        self.description = soup.find(
            "div", class_="dotd-main-book-summary float-left").select(
            "div")[2].text.strip()
        dotd_image = soup.find("div", class_="dotd-main-book-image float-left")
        self.image_src = "https:" + dotd_image.a.noscript.img.get('src')
        dt = datetime.now()
        self.date = dt.strftime("%Y-%m-%d %H:%M")

        return self

    def json(self):
        return({"date": self.date,
                "title": self.title,
                "description": self.description,
                "image_src": self.image_src
                })
