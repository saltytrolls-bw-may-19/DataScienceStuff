""" 
Main application and routing logic
 for hosting in docker containers
"""
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
    return (json_out)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
