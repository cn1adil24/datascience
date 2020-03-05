import requests
import json
from datetime import date, datetime, timedelta
import sys

url = "http://ec2-3-84-42-90.compute-1.amazonaws.com:4000/search"
headers = {
    'Content-Type': "application/json",
    'cache-control': "no-cache",
    'Postman-Token': "198a5cfc-424f-46d1-b239-6ef2dbab28c2"
}
maxResults = 100
today = str(date.today())

if __name__ == "__main__":
    
    keyword = ""
    flag = False
    for word in sys.argv:
        if not flag:
            flag = True
            continue
        keyword += word + " "

    keyword = keyword.rstrip()
    
    payload = "{\n\t\"tag\":\"author\",\n\t\"smpList\": [\n\t\t{\n\t\t\t\"name\":\"twitter\",\n\t\t\t\"params\": {\n\t\t\t\t\"q\":\""+keyword+"\",\n\t\t\t\t\"count\":"+str(maxResults)+",\n\t\t\t\t\"tweet_mode\":\"extended\"\n\t\t\t,\n\t\t\t\t\"lang\":\"en\",\n\t\t\t\t\"place_country\":\"ISO 3166-2:PK\"\n\t\t\t}\n\t\t}\n\t]\n}"

    response = requests.request("POST", url, data=payload, headers=headers)

    response_json = response.json()

    data = response_json[0]['statuses']

    ss = today

    print("Retrieved "+ str(len(data)) + " tweets on " + str(ss) + " Keyword: " + keyword)

    file = 'tweets/tweet-' + keyword + '_date_' + ss + '.txt'
    with open(file, 'w') as outfile:
        json.dump(data, outfile)