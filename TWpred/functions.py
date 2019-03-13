# pip install google-cloud-bigquery
# pip install pandas
# pip install textblob
import re
import sys
import pandas as pd
from textblob import TextBlob
from google.cloud import bigquery
from TWpred.twitter_API import *


def adduser(tw_handle):
   #   Get TW user info 
   twitter_user = TWITTER.get_user(tw_handle)

   #  get their tweets from TW timeline
   tweets = twitter_user.timeline(count=200, exclude_replies=True, include_rts=False, tweet_mode='extended')

   # create a DB User -  use the model.py class
   db_user = User(id=twitter_user.id, name=twitter_user.screen_name, newest_tweet_id=tweets[0].id)

   # load the tweets
   for tweet in tweets:
      embedding = BASILICA.embed_sentence(tweet.full_text, model='twitter')
      db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:500], embedding=embedding)
      DB.session.add(db_tweet)        #  add the tweets to the DB first
      db_user.tweets.append(db_tweet) # then connect/append to the user
   
   DB.session.add(db_user)  # can this be done earlier??
   DB.session.commit()
   #------
   return


def add_or_update_user(username):

   """Add or update a user *and* their Tweets, error if no/private user."""
   try:
      twitter_user = TWITTER.get_user(username)
      #  if userId exists .get it  or if not create one 
      db_user = (User.query.get(twitter_user.id) or
                  User(id=twitter_user.id, name=username))
      DB.session.add(db_user)
      # We want as many recent non-retweet/reply statuses as we can get
      tweets = twitter_user.timeline(
         count=200, exclude_replies=True, include_rts=False,
         tweet_mode='extended', since_id=db_user.newest_tweet_id)
      if tweets:
         db_user.newest_tweet_id = tweets[0].id
      for tweet in tweets:
         # Get embedding for tweet, and store in db
         embedding = BASILICA.embed_sentence(tweet.full_text,
                                             model='twitter')
         db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:500],
                           embedding=embedding)
         db_user.tweets.append(db_tweet)
         DB.session.add(db_tweet)
   except Exception as e:
      print('Error processing {}: {}'.format(username, e))
      raise e
   else:
      DB.session.commit()

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
    iterator = query_job.result(timeout=30)
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
