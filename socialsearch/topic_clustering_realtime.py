# coding: utf-8

from gensim.models import Word2Vec
import nltk
from sklearn.cluster import KMeans
from sklearn import cluster
from sklearn import metrics
from sklearn.decomposition import PCA
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import json
import os
import re
import preprocessor as p
from nltk import FreqDist
from nltk.stem import WordNetLemmatizer, SnowballStemmer
import matplotlib.pyplot as plt
import seaborn as sns
import gensim
import sys
import pickle

twitter_dest = "tweets/"
youtube_dest = "videos/"

if __name__ == "__main__":

    keyword = ""
    flag = False
    for word in sys.argv:
        if not flag:
            flag = True
            continue
        keyword += word + " "

    keyword = keyword.rstrip()

    twitter_all_files = os.listdir(twitter_dest)
    youtube_all_files = os.listdir(youtube_dest)

    twitter_files = []
    youtube_files = []

    for file in twitter_all_files:
        if keyword in file:
            twitter_files.append(file)
            
    for file in youtube_all_files:
        if keyword in file:
            youtube_files.append(file)


    ##### Loading Twitter JSON files

    twitter_json = []

    for file in twitter_files:
        with open(twitter_dest + file) as json_file:
            
            # Load file
            data = json.load(json_file)
            
            # Concatenate all files
            twitter_json = twitter_json + data
        
    
    ##### Loading YouTube JSON files

    yt_json = []

    for file in youtube_files:
        with open(youtube_dest + file) as json_file:
            
            # Load file
            data = json.load(json_file)        
            
            # Concatenate all files
            yt_json = yt_json + data
        
    
    ##### Retrieving relevant information from the Twitter JSON objects

    columns = ['Created_time', 'URL', 'User_name', 'Twitter_handle', 'Description', 'Retweet_count', 'Favorite_count', 'Sentiment', 'Topic']
    df_tweets = pd.DataFrame(columns=columns)

    for i in range(0, len(twitter_json)):
        
        Created_time = twitter_json[i]['created_at']
        
        URL = 'twitter.com/i/web/status/' + twitter_json[i]['id_str']
        
        User_name = twitter_json[i]['user']['name']
        
        Twitter_handle = twitter_json[i]['user']['screen_name']
        
        if 'retweeted_status' not in twitter_json[i]:
            Description = twitter_json[i]['full_text']
        else:
            Description = twitter_json[i]['retweeted_status']['full_text']
        
        Retweet_count = twitter_json[i]['retweet_count']
        
        Favorite_count = twitter_json[i]['favorite_count']
        
        Sentiment = twitter_json[i]['sentiment']
        
        df_tweets = df_tweets.append({'Created_time':Created_time,'URL':URL,'User_name':User_name,
                                      'Twitter_handle':Twitter_handle,'Description':Description,
                                      'Retweet_count':Retweet_count,'Favorite_count':Favorite_count,
                                      'Sentiment':Sentiment, 'Topic':np.nan}, ignore_index=True)
        
    ##### Retrieving relevant information from the Youtube JSON objects

    ss=r'([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))'
    columns = ['Published_date', 'Title', 'URL', 'Channel_id', 'Topic']
    df_videos = pd.DataFrame(columns=columns)

    for i in range(0, len(yt_json)):
        
        Published_date = re.findall(ss,yt_json[i]['snippet']['publishedAt'])[0][0]
        
        Title = yt_json[i]['snippet']['title']
        
        Channel_id = yt_json[i]['snippet']['channelId']
        
        URL = 'https://www.youtube.com/watch?v=' + yt_json[i]['id']['videoId']
        
        df_videos = df_videos.append({'Published_date':Published_date,'Title':Title,
                                      'Channel_id':Channel_id,'URL':URL, 'Topic':np.nan}, ignore_index=True)

    ##### Added temporary column for processing 

    df_tweets['cleaned'] = np.nan
    df_videos['cleaned'] = df_videos['Title']


    ##### Preprocessing Tweets

    def isEnglish(s):
        try:
            s.encode('ascii')
        except UnicodeEncodeError:
            return False
        else:
            return True


    ##### Set options to be removed

    #p.set_options(p.OPT.URL, p.OPT.EMOJI, p.OPT.HASHTAG)
    p.set_options(p.OPT.URL, p.OPT.EMOJI)

    for i in range(0, len(df_tweets)):
        
        # Clean URLs, Emojis, Hashtags
        df_tweets['cleaned'][i] = p.clean(df_tweets['Description'][i])
        
        # Remove '@' without removing the username
        df_tweets['cleaned'][i] = re.sub('@', ' ', df_tweets['cleaned'][i])
        
        # Remove '#' without removing the username
        df_tweets['cleaned'][i] = re.sub('#', ' ', df_tweets['cleaned'][i])
        
        #Remove all unicode(non-English) tweets
        x = df_tweets['cleaned'][i]
        x = x.replace('…', '')
        x = x.replace('‘', '')
        x = x.replace('’', '')
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
        x = emoji_pattern.sub(r'', x)        
        if isEnglish(x):
            df_tweets['cleaned'][i] = x
        else:
            df_tweets['cleaned'][i] = np.nan

    df_tweets.dropna(subset=['cleaned'], inplace=True)


    ##### dropping ALL duplicate values 

    df_tweets.drop_duplicates(subset ="Description", 
                         keep = 'first', inplace = True)

    # Reset index
    df_tweets = df_tweets.reset_index(drop=True)

    
    ##### remove unwanted characters, numbers and symbols

    df_tweets['cleaned'] = df_tweets['cleaned'].str.replace("[^a-zA-Z]", " ")
    df_tweets['cleaned'] = df_tweets['cleaned'].str.replace('&amp;', " ")
    df_tweets['cleaned'] = df_tweets['cleaned'].str.replace('amp', " ")

    df_videos['cleaned'] = df_videos['cleaned'].str.replace("[^a-zA-Z]", " ")
    df_videos['cleaned'] = df_videos['cleaned'].str.replace("SAMAA TV", " ")
    df_videos['cleaned'] = df_videos['cleaned'].str.replace("BBC", " ")
    df_videos['cleaned'] = df_videos['cleaned'].str.replace("Dunya", " ")
    df_videos['cleaned'] = df_videos['cleaned'].str.replace("News", " ")
    df_videos['cleaned'] = df_videos['cleaned'].str.replace("Headlines", " ")
    df_videos['cleaned'] = df_videos['cleaned'].str.replace("&amp;", " ")
    df_videos['cleaned'] = df_videos['cleaned'].str.replace("amp", " ")


    ##### Remove all Roman Urdu words

    words = set(nltk.corpus.words.words())

    for i in range(0, len(df_tweets)):
        text = df_tweets['cleaned'][i]
        cleaned = ""
        for w in nltk.wordpunct_tokenize(text):
            if w.lower() in words and w.isalpha():
                cleaned = cleaned + w + ' '
        df_tweets['cleaned'][i] = cleaned


    ##### Remove short tweets

    i = 0
    l = len(df_tweets)
    while i < l:
        w = df_tweets['Description'][i].split()
        if len(w) <= 3:
            df_tweets = df_tweets.drop(df_tweets.index[i])
            df_tweets = df_tweets.reset_index(drop=True)
        i = i + 1
        l = len(df_tweets)

    
    ##### Text Preprocessing

    stop_words = stopwords.words('english')


    ##### function to remove stopwords

    def remove_stopwords(rev):
        rev_new = " ".join([i for i in rev if i not in stop_words])
        return rev_new


    ##### remove short words (length < 3)

    df_tweets['cleaned'] = df_tweets['cleaned'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>2]))

    df_videos['cleaned'] = df_videos['cleaned'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>2]))


    ##### remove stopwords from the text

    tweets = [remove_stopwords(r.split()) for r in df_tweets['cleaned']]

    videos = [remove_stopwords(r.split()) for r in df_videos['cleaned']]

    
    ##### Convert letters into lower case

    tweets = [r.lower() for r in tweets]

    videos = [r.lower() for r in videos]


    for word in keyword.split():
        tweets = [r.replace(word, " ") for r in tweets]


    ##### Stemming and lemmatization functions

    def lemmatize_stemming(text):
        stemmer = SnowballStemmer("english")
        return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

    def preprocess(text):
        result = []
        for token in gensim.utils.simple_preprocess(text):
            result.append(lemmatize_stemming(token))            
        return result


    ##### Temporary dataframe for mapping lemmatized texts

    tweets_1 = pd.DataFrame(tweets, columns=['text'])

    videos_1 = pd.DataFrame(videos, columns=['title'])


    ##### Extracting lemmatized words

    processed_tweets = tweets_1['text'].map(preprocess)

    processed_videos = videos_1['title'].map(preprocess)

    ##### For tokenizing words from tweets

    tokenized_tweets = []
    for tweet in processed_tweets:
        tokenized_tweets.append(tweet)


    ##### For tokenizing words from videos

    tokenized_videos = []
    for video in processed_videos:
        tokenized_videos.append(video)
        
    

    ##### Creating the Word2Vec model


    model = Word2Vec(tokenized_tweets, size=2, min_count=1)

    def vectorizer(sent, m):
        vec = []
        numw = 0
        for w in sent:
            try:
                if numw == 0:
                    vec = m[w]
                else:
                    vec = np.add(vec, m[w])
                numw += 1
            except:
                pass
        
        return np.asarray(vec, dtype=np.float) / numw

    l = []

    for i in tokenized_tweets:
        l.append(vectorizer(i, model))

    #X = model[model.wv.vocab]
    X = np.array(l)


    ##### K-Means Clustering
    
    for i in range(len(X)):
        if len(X[i]) == 0:
            X[i] = np.nan
    
    output = []
    tokenized_tweets_new = []
    i = 0
    for elem in X:
        if elem is not np.nan:
            output.append(elem)
            tokenized_tweets_new.append(tokenized_tweets[i])
        else:
            df_tweets = df_tweets.drop(df_tweets.index[i])
        i += 1

    df_tweets = df_tweets.reset_index(drop=True)
    X = np.array(output)
    tokenized_tweets = tokenized_tweets_new
    
    # No. of clusters
    n_clusters = 5
    clf = KMeans(n_clusters = n_clusters, max_iter = 100, init = 'k-means++', n_init = 1)
    labels = clf.fit_predict(X)


    ###### Assigning topics to tweets:

    i = 0
    for index, sentence in enumerate(tokenized_tweets):
        
        df_tweets['Topic'][i] = int(labels[index])
        
        i += 1


    ##### Clustering videos and assigning topics to videos

    model = Word2Vec(tokenized_videos, size=2, min_count=1)
    l = []
    for i in tokenized_videos:
        l.append(vectorizer(i, model))
    X = np.array(l)

    for i in range(len(X)):
        if len(X[i]) == 0:
            X[i] = np.nan

    output = []
    tokenized_videos_new = []
    i = 0
    for elem in X:
        if elem is not np.nan:
            output.append(elem)
            tokenized_videos_new.append(tokenized_videos[i])
        else:
            df_videos = df_videos.drop(df_videos.index[i])
        i += 1

    df_videos = df_videos.reset_index(drop=True)
    X = np.array(output)
    tokenized_videos = tokenized_videos_new
    
    labels = clf.predict(X)

    i = 0
    for index, sentence in enumerate(tokenized_videos):
        
        df_videos['Topic'][i] = int(labels[index])
        
        i += 1


    ###### Drop the temporary columns

    df_tweets = df_tweets.drop(['cleaned'], axis=1)
    df_videos = df_videos.drop(['cleaned'], axis=1)


    ##### Export twitter data to json format for further processing

    df_to_json_tweets = df_tweets.to_dict('records')
    file = r'model\topic-tweets_' + keyword + '_' + str(n_clusters) + '_topics.json'
    with open(file, 'w') as outfile:
        json.dump(df_to_json_tweets, outfile)

    ##### Export youtube data to json format for further processing

    df_to_json_videos = df_videos.to_dict('records')
    file = r'model\topic-videos_' + keyword + '_' + str(n_clusters) + '_topics.json'
    with open(file, 'w') as outfile:
        json.dump(df_to_json_videos, outfile)


    ##### Saving model

    filename = 'cluster/kmeans-'+keyword+'.sav'
    pickle.dump(clf, open(filename, 'wb'))


    ##### Loading model

    #loaded_model = pickle.load(open(filename, 'rb'))
    #result = loaded_model.score(X_test, Y_test)
    #print(result)