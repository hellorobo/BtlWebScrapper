from flask_restful import Resource
from models.btlscrapper import EbookModel


class Ebook(Resource):

    def get(self):
        url = 'https://www.microsoft.com/en-us/learning/community-blog.aspx'

        result = EbookModel().get(url)
        return result.json()
