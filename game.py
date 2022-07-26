import datetime
from dateutil import parser, tz
import requests
import json


# Query by date (ex: 2022-05-09), league(NBA, NHL), tea
ex = 'http://sdn-bet-api.us-east-1.elasticbeanstalk.com/games'
ex1 = 'http://sdn-bet-api.us-east-1.elasticbeanstalk.com/games?league=NBA&date=2022-05-09'
ex2 = 'http://sdn-bet-api.us-east-1.elasticbeanstalk.com/games?league=NBA&date=2022-05-09&team=Milwaukee Bucks'


# Get request to load into json data
def get_response_json(url):
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data = payload)
    #print(response.text)
    try:
        data = json.loads(response.text) if response.text else {}
        #print('try success')
        return {'data': data, 'status_code': response.status_code}
    except:
        return {'data': 'request failed', 'status_code': response.status_code}

url = ex
