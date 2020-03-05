from apiclient.discovery import build
from datetime import date
import json
import re
import sys

api_key = 'AIzaSyDrFEl1ySRgTw-p4SdHAWwaQ4dsiVLGFgk'
maxResults = 50
today = str(date.today())
youtube = build('youtube', 'v3', developerKey = api_key)
date_re = r"([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))"

if __name__ == "__main__":
    
    keyword = ""
    flag = False
    for word in sys.argv:
        if not flag:
            flag = True
            continue
        keyword += word + " "

    keyword = keyword.rstrip()
    
    # Set criteria
    req = youtube.search().list(q=keyword, part='snippet', type='video', maxResults=maxResults,
                                    publishedAfter=today+'T00:00:00Z', location="30.3753, 69.3451", locationRadius = "500mi")

    # Execute request
    res = req.execute()

    data = res['items']

    print("Retrieved " + str(len(res['items'])) + " videos on " + today + " Keyword: " + keyword)

    file = 'videos/video-' + keyword + '_date_' + today + '.txt'
    with open(file, 'w') as outfile:
        json.dump(data, outfile)