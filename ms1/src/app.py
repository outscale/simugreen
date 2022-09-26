import configparser
import psycopg2
from flask import Flask, jsonify, request
from marshmallow import ValidationError

from .schema import OutputSchema

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.cfg')

conn = psycopg2.connect(
        host=config['POSTGRES']['Host'],
        database=config['POSTGRES']['Database'],
        user=config['POSTGRES']['User'],
        password=config['POSTGRES']['Password'])

@app.route("/")
def hello_world():
    return "<p>Welcome to the hackaton app.</p>"

@app.route('/send_output', methods=['POST'])
def send_output():
    
    request_data = request.json
    schema = OutputSchema()

    #Check that the form contains the requested fields
    try:
        result = schema.load(request_data)
    
    # Otherwise throw a 400 error
    except ValidationError as err:
        print("Unvalid json")
        return jsonify(err.messages), 400

    cur = conn.cursor()
    conn.commit()
    cur.close()
    
    #-> Check that the id exist inside the Db
    return "<p>Output Succesfully return</p>"