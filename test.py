import pymongo


dbuser = 'user1'
dbpass = 'vJYD#zjn52?JTGre8mCJ'

connection = pymongo.MongoClient('mongodb://user1:vJYD#zjn52?JTGre8mCJ@ds117070.mlab.com:17070/webscrap01')
db = connection.webscrap01
posts_col = db.btl_posts

match = 'Microsoft Learning Community: Take a tour of our new space'
'''
postFound = posts_col.find_one({'post': match})

print('postFound: {}'.format(postFound))
if postFound == None:
    try: 
        result = posts_col.insert_one({'post': match})
    except Exception as e:
        print("Exception: ", type(e), e)
    print('post inserted? {}'.format(result.acknowledged))

'''
try: 
       result = posts_col.find_one_and_replace(
                                       filter={'post': match},
                                       replacement={'post': match},
                                       upsert=True
                                       )
except Exception as e:
    print("Exception: ", type(e), e)

if  not pymongo.ReturnDocument.BEFORE: print('new document inserted: {}'.format(result['_id']))
