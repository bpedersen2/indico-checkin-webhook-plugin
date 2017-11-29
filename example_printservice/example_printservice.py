#/usr/bin/env python
"""Example print service endpoint for the indico checkin webhook plugin


to run:
FLASK_APP=example_printservice.py flask run
"""

from flask import Flask
from flask import request
from flask.json import loads
from werkzeug.utils import secure_filename
import socket

from pprint import pprint
#
config = {'printer': 'localhost'}

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, Printer Proxy!'


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        sendToPrinter(f)
    return 'success'


@app.route('/json', methods=['GET', 'POST'])
def upload_json():
    if request.method == 'POST':
        data = request.get_json()
        pprint(data)
    return 'success'


@app.route('/combined', methods=['GET', 'POST'])
def combined_endpoint():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        sendToPrinter(f)
        data = loads(request.form['data'])
        pprint(data)

    return 'success'


def sendToPrinter(stream):
    try:
        printer = socket.socket()
        printer.connect((config['printer'], 9100))
        printer.send(stream)
        printer.close()
    except socket.error:
        return False
