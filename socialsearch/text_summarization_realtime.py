from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import distance
from nltk.translate.bleu_score import sentence_bleu
import pandas as pd
from gensim.summarization.summarizer import summarize
import json
from datetime import datetime
import sys

if __name__ == "__main__":

    keyword = ""
    flag = False
    for word in sys.argv:
        if not flag:
            flag = True
            continue
        keyword += word + " "

    keyword = keyword.rstrip()

    ##### Read the file assigned with topics

    df = pd.read_json('model/topic-tweets_'+keyword+'_5_topics.json')
    
    df = df.reset_index(drop=True)


    ##### Extract top 5 tweets from each topic

    unique = set(df['Topic'])

    no_of_topics = 5

    df_topic = []

    for i in range(0, no_of_topics):
        if i not in unique:
            continue
        df_i = df.loc[df['Topic']==i]
        x = df_i.nlargest(5, ['Retweet_count'])
        x = x.reset_index()
        if len(x) < 5:
            unique.remove(i)
        else:
            df_topic.append(x)
        
    
    ##### Generate summaries of each topic

    summaries = []

    for j in range(0, len(df_topic)):        

        topic = ""
        
        # Extract tweet of particular topic
        
        for i in range(0, len(df_topic[j])):
            topic += df_topic[j]['Description'][i] + '. '
            
        # Summarize using gensim.summarize
        
        summary = summarize(text=topic, ratio=0.25, split=True)
        
        # Filter out duplicate sentences
        
        filtered = list(dict.fromkeys(summary))
        
        ss = ""
        for i in range(0, len(filtered)):
            ss += filtered[i]
        
        summaries.append(ss)


    ##### Get overall sentiment & time of summary

    sentiment = []
    dates = []
    x = 0

    for j in range(0, no_of_topics):
        
        if j not in unique:
            continue

        sent = []
        
        # Extract tweet of particular topic
        
        for i in range(0, len(df)):
            if df['Topic'][i].astype(int) == j:
                sent.append(df['Sentiment'][i])
        
        m = max(sent, key=sent.count)
        sentiment.append(m)
        
        d = df_topic[x]['Created_time'][0]
        d = datetime.strptime(str(d), '%Y-%m-%d %H:%M:%S')
        dates.append(str(d.date()))
        x += 1

    
    ##### Convert list to dataframe

    summary_df = pd.DataFrame({"Summary":summaries,"Sentiment":sentiment,"Date":dates})
    summary_df = summary_df.reset_index()

    ##### Add Topic column to each summary

    summary_df.rename(columns={'index':'topic'}, inplace=True)
    

    ##### Save summaries to json format

    summary_json = summary_df.to_dict('records')
    
    file = r'model\summary_' + keyword + '_5_topics.json'
    with open(file, 'w') as outfile:
        json.dump(summary_json, outfile)