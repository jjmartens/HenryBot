import requests
import time
import re
import sqlalchemy
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

engine = create_engine('mysql://root:@localhost/henry?charset=utf8', pool_recycle=3600,encoding='utf-8')
Base = declarative_base()
session = Session(engine)
class Response(Base):
     __tablename__ = 'Response'

     id = Column(Integer, primary_key=True)
     trigger = Column(String)
     response = Column(String)
     def __init__(self, trigger,response):
         self.trigger = trigger
         self.response = response

     def __repr__(self):
        return "<Response(trigger='%s', response='%s')>" % (
                             self.trigger, self.response)

API_KEY = os.environ['HENRY_API_KEY']

dict = {}

def parse_message(msg, data):
    if 'username' in data['message']['from']:
        username = "@" + data['message']['from']['username']
    elif 'first_name' in data['message']['from']:
        username = data['message']['from']['first_name']
    else:
        username = 'Unknown'
    return msg.replace("{user}", username)

def parse_response(json):
    if 'text' in json['message']:
        match = re.search(r'(\w+):([^:]+):(.+)', json['message']['text'])
        if match is not None:
            if(match.group(1) == "add"):
                pattern = match.group(2)
                answer = match.group(3)
                if len(pattern) > 2:
                    dict[pattern.upper()] = answer
                    session.add(Response(pattern.upper(),answer))
                    session.commit()
            elif match.group(1) == "henry":
                if match.group(2) == "delete":
                    pattern = match.group(3)[:-1]
                    pattern_capi = pattern.upper()
                    if pattern_capi in dict.keys():
                        dict.pop(pattern_capi)
                        responses = session.query(Response).filter_by(trigger=pattern).all()
                        for res in responses:
                            session.delete(res)
                        session.commit()
                elif match.group(2) == "dump":
                    requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(API_KEY, json['message']['chat']['id'], "\n".join(map(str,dict.keys())).encode('utf8')))
        else:
            answer = ""
            for key in dict.keys():
                pre = r'((ge)|(ver)|(in)|(on)|(non)|(wan))?'
                rex = r'(^|[?!.,:;\s]+)(' + pre + key + r')+[?!.,:;]*($|((\s.*)+))'
                match = re.search(rex, json['message']['text'].upper(), re.IGNORECASE)
                if match:
                    answer += dict[key]
                    answer += "\n"

            if answer != "":
                requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(API_KEY, json['message']['chat']['id'], parse_message(answer,json).encode('utf8')))


def loop(id = 0):
    data = requests.get("https://api.telegram.org/bot{}/getUpdates?offset={}&timeout=30".format(API_KEY, id))
    data.encoding = 'utf8'
    if data is not None:
        json = data.json(encoding='utf8')
        result = json['result']
        if len(result) > 0:
            id = result[0]['update_id']
            parse_response(result[0])
    return id

if __name__ == '__main__':
    q = session.query(Response).all()
    for response in q:
        dict[response.trigger.upper()] = response.response
    id = 0
    while True:
        id = loop(id) + 1
