""" Main application and routing logic for TweetR """
from flask import Flask, request, render_template
from .models import DB, User, Tweet
from decouple import config
from .functions import textblob_sentiment
from .predicted import predict_user
import re
import sys
import pandas as pd
from textblob import TextBlob
from google.cloud import bigquery

def create_app():
    """ create + config Flask app obj """
    app = Flask(__name__)

    #  after creatin models.py  run the follow
    #  configure the app object 
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')  # get db loc from .env
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    client = bigquery.Client
    @app.route('/')
    def root():
        return render_template('base.html', title='Home')

    #@app.route('/user', methods=['POST'])
    @app.route('/user/<name>')
    def user(name=None):
        message = ''
        json_out = textblob_sentiment(name)
        return json_out
        # return render_template('user.html', title=name, message=message)

    return app

       
#  to run from terminal : cd to TWpred subfolder (where app.py resides)
#                         set FLASK_APP=TWpred:APP
#                   +     flask run   OR    flask shell

 