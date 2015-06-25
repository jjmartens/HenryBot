import requests
import time
import re
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String

engine = create_engine('mysql://root:@localhost/henry', pool_recycle=3600)
Base = declarative_base()

class Response(Base):
     __tablename__ = 'users'

     id = Column(Integer, primary_key=True)
     trigger = Column(String)
     response = Column(String)
     def __init(self, trigger,response):
         self.trigger = trigger
         self.response = response

     def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
                             self.name, self.fullname, self.password)

API_KEY = "<GECENSUREERD>"

dict = {}
def parse_response(json):
    if 'text' in json['message']:
        match = re.search(r'(\w+):(\w+):(.+)', json['message']['text'])
        if match is not None:
            if(match.group(1) == "add"):
                pattern = match.group(2)
                answer = match.group(3)
                if len(pattern)> 3:
                    dict[pattern] = answer

        for key in dict.keys():
            if key in json['message']['text']:
                requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(API_KEY, json['message']['chat']['id'], dict[key]))


def loop(id = 0):
    data = requests.get("https://api.telegram.org/bot{}/getUpdates?offset={}&timeout=30".format(API_KEY, id))
    json = data.json()
    result = json['result']
    if len(result) > 0:
        id = result[0]['update_id']
        parse_response(result[0])
    time.sleep(0.2)
    loop(id + 1)

if __name__ == '__main__':
    loop()

