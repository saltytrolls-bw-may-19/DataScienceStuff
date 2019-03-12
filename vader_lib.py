# pip install google-cloud-bigquery
# pip install pandas
# pip install nltk

import sys
from google.cloud import bigquery
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

#  authenticate with google
jsonPath = "google-cred.json"
client = bigquery.Client.from_service_account_json(jsonPath)


def vader_sentiment(author):
    #  Construct SQL query
    #  Using WHERE reduces the amount of data scanned / quota used
    query = """
    SELECT author, time, text, ranking
    FROM `bigquery-public-data.hacker_news.comments`
    """
    query = query + 'WHERE author = "'+author+'"'
    query = query + 'LIMIT 10'
    

    # TODO  needs  TRY / CATCH
    query_job = client.query(query)
    # -------------------------------

    iterator = query_job.result(timeout=30)
    rows = list(iterator)

    # Transform the rows into dataframe
    headlines = pd.DataFrame(data=[list(x.values()) for x in rows],
                             columns=list(rows[0].keys()))
    
    
    comments = headlines['text']
    analyzer = SentimentIntensityAnalyzer()
    for comment in comments:
        vs = analyzer.polarity_scores(comment)
        print(vs)
        # print("{:-<65} {}".format(comment, str(vs)))
    return


def main():
    auth = sys.argv[1] 
    vader_sentiment()

#  Launched from the command line
if __name__ == '__main__':
    main(sys.argv[1])

