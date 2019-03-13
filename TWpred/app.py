""" Main application and routing logic for TweetR """
from flask import Flask, request, render_template
from functions import textblob_sentiment
from flask_cors import CORS

""" create + config Flask app obj """
app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    return render_template('base.html', title='Home')

@app.route('/user/<name>')
def user(name=None):
    json_out = textblob_sentiment(name)
    return json_out

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

#  to run from terminal : cd to TWpred subfolder (where app.py resides)
#                         set FLASK_APP=TWpred:APP
#                   +     flask run   OR    flask shell
