""" Main application and routing logic for TweetR """
from flask import Flask, request, render_template
from .functions import textblob_sentiment

def create_app():
    """ create + config Flask app obj """
    app = Flask(__name__)

    @app.route('/')
    def root():
        return render_template('base.html', title='Home')

    @app.route('/user/<name>')
    def user(name=None):
        json_out = textblob_sentiment(name)
        return json_out
    return app
       
#  to run from terminal : cd to TWpred subfolder (where app.py resides)
#                         set FLASK_APP=TWpred:APP
#                   +     flask run   OR    flask shell
