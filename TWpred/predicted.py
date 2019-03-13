"""Prediction of Users based on Tweet embeddings."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from .models import User
from .twitter_API import BASILICA

# See video :https://www.youtube.com/watch?v=zwtwTdNqrBA&t=3908s&index=4&list=PL2SsOkMTK8FCZNQFZW6XlzVxBTHAtdhmU
# @ 1:11:00
def predict_user(user1_name, user2_name, tweet_text):
    """Determine and return which user is more likely to say a given Tweet."""
    ''' returns 0 if morelikely said by user 1 , 1 if user_2'''

    user1 = User.query.filter(User.name == user1_name).one()
    user2 = User.query.filter(User.name == user2_name).one()
    user1_embeddings = np.array([tweet.embedding for tweet in user1.tweets])
    user2_embeddings = np.array([tweet.embedding for tweet in user2.tweets])
    embeddings = np.vstack([user1_embeddings, user2_embeddings])
    labels = np.concatenate([np.zeros(len(user1.tweets)),
                             np.ones(len(user2.tweets))])
    log_reg = LogisticRegression().fit(embeddings, labels)
    tweet_embedding = BASILICA.embed_sentence(tweet_text, model='twitter')

    ## import pdb; pdb.set_trace() #  launch debug 

    return log_reg.predict(np.array(tweet_embedding).reshape(1, -1))