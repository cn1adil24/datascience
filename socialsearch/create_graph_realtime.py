from py2neo import Graph
from py2neo import Node, Relationship
import json
import pandas as pd
import sys

graph = Graph('http://localhost:7474', password='1234')

if __name__ == "__main__":

    keyword = ""
    flag = False
    for word in sys.argv:
        if not flag:
            flag = True
            continue
        keyword += word + " "

    keyword = keyword.rstrip()
    
    file = 'model/summary_' + keyword + '_5_topics.json'
    twitter_file = 'model/topic-tweets_' + keyword + '_5_topics.json'
    #youtube_file = 'model/topic-videos_' + keyword + '_5_topics.json'
    
    with open(twitter_file) as json_file:
        tweet_data = json.load(json_file)
        
    #with open(youtube_file) as json_file:
    #    yt_data = json.load(json_file)
    
    
    # Create an entity
    entity = Node("Entity", name = keyword)
    
    graph.create(entity)

    # Creating summaries

    with open(file) as json_file:
        data = json.load(json_file)

    for i in range(0, len(data)):

        summary = Node("Summary", Topic=data[i]['topic']
                             , Summary=data[i]['Summary']
                             , Sentiment=data[i]['Sentiment']
                             , Date=data[i]['Date'])

        graph.create(summary)

        r = Relationship(entity, "HAS_STORY", summary)

        graph.create(r)
        
        # Creating tweets and videos belonging to that summary
    
        for j in range(0, len(tweet_data)):
            if tweet_data[j]['Topic'] == i:
                tweet = Node("Tweet", Created_time = tweet_data[j]['Created_time']
                                    , URL = tweet_data[j]['URL']
                                    , User_name = tweet_data[j]['User_name']
                                    , Twitter_handle = tweet_data[j]['Twitter_handle']
                                    , Description = tweet_data[j]['Description']
                                    , Retweet_count = tweet_data[j]['Retweet_count']
                                    , Favorite_count = tweet_data[j]['Favorite_count']
                                    , Sentiment = tweet_data[j]['Sentiment']
                                    , Topic = tweet_data[j]['Topic'])
                graph.create(tweet)

                r = Relationship(summary, "HAS_TWEET", tweet)

                graph.create(r)
    
        '''
        for j in range(0, len(yt_data)):
            if yt_data[j]['Topic'] == i:
                video = Node("Video", Published_date = yt_data[j]['Published_date']
                                    , Title = yt_data[j]['Title']
                                    , URL = yt_data[j]['URL']
                                    , Channel_id = yt_data[j]['Channel_id']
                                    , Topic = yt_data[j]['Topic'])

                graph.create(video)

                r = Relationship(summary, "HAS_VIDEO", video)

                graph.create(r)
        '''