# pip install google-cloud-bigquery
# pip install pandas
# pip install textblob
import re
import sys
import pandas as pd
from textblob import TextBlob
from google.cloud import bigquery


def clean_text(text):
    """
    Utility function to clean text by removing links, special characters
    using simple regex statements. May not be needed.
    """
    return ''.join(re.sub(r'(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\ / \ / \S+)', '', text))


def get_sentiment(text):
    """
    Utility function to classify sentiment of passed text
    using textblob's sentiment method. Return the polarity
    score as a float within the range [-1.0, 1.0]
    """
    # create TextBlob object of passed text's polarity
    return TextBlob(text).sentiment.polarity


def textblob_sentiment(author):
    # LOCAL authenticate with google
    jsonPath = "env.py"
    client = bigquery.Client.from_service_account_json(jsonPath)
    
    # HEROKU  authenticate with google ->  uses config vars in dashboard
    #client = bigquery.Client()
    
    # Construct SQL query
    # Using WHERE reduces the amount of data scanned / quota used
    query = """
    SELECT author, time, text, ranking
    FROM `bigquery-public-data.hacker_news.comments`
    """
    query = query + 'WHERE author = "'+author+'"'

    # submit query and make a list of results
    query_job = client.query(query)
    iterator = query_job.result(timeout=90)
    rows = list(iterator)

    # Exception handling:  bug out if no comments found
    if len(rows) < 1:
        return ('Commenter '+author+' not found')

    # Transform the rows into dataframe
    df = pd.DataFrame(data=[list(x.values()) for x in rows],
                      columns=list(rows[0].keys()))

    # Generate the sentiment analysis for each cleaned comment.
    df['comment'] = df.text.apply(lambda x: clean_text(x))
    df['sentiment'] = df.comment.apply(lambda x: get_sentiment(x))
    df = df.sort_values(by=['sentiment'], ascending=True)

    # Output 1: Username + Overall Sentiment + Num of Comments
    #  (Mean of all comment sentiment, unweighted.)
    output1 = df.groupby('author', as_index=False)[['sentiment']].mean()
    dfJSON = output1.to_json(orient='records')
    output1JSON = dfJSON[0:-2]
    output1JSON = output1JSON + ',"num_comments":' + str(len(df)) + '}]'

    # Output 2: Top 10 Saltiest Records
    output2 = df[['author', 'sentiment', 'ranking', 'time', 'comment']][0:9]
    output2JSON = output2.to_json(orient='records')
    
    # may have to output as stdout for node.js integration
    # print (output1JSON, output2JSON)
    # sys.stdout.flush()

    return (output1JSON + output2JSON)
