import requests
import time

API_KEY = "bot110574668:AAFWistE1uWqzrcqryg9U08FgYj7P94wBDo"

def parse_response(json):
    if 'text' in json['message']:
        if "geld" in json['message']['text']:
            requests.get("https://api.telegram.org/{}/sendMessage?chat_id={}&text=Geld?! je hebt nooit geen geld!".format(API_KEY, json['message']['chat']['id']))
        if "willem" in json['message']['text']:
            requests.get("https://api.telegram.org/{}/sendMessage?chat_id={}&text=Willem?! bedoel je Willy?".format(API_KEY, json['message']['chat']['id']))



def loop(id = 0):
    data = requests.get("https://api.telegram.org/{}/getUpdates?offset={}&timeout=30".format(API_KEY, id))
    json = data.json()
    result = json['result']
    if len(result) > 0:
        id = result[0]['update_id']
        parse_response(result[0])
    time.sleep(0.2)
    loop(id + 1)

if __name__ == '__main__':
    loop()

