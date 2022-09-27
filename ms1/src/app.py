import psycopg2
from flask import Flask, jsonify, request

HOST = "db1"
DATABASE = "postgres"
USERNAME = "postgres"
PASSWORD = "postgres"

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Welcome to the hackaton app!</p>"


@app.route('/test')
def test():
    return "test"

@app.route('/method1', methods=['GET'])
def method1():

    try:
        conn = psycopg2.connect(
            host=HOST,
            database=DATABASE,
            user=USERNAME,
            password=PASSWORD)

        cur = conn.cursor()
        cur.execute("""SELECT * FROM quote LIMIT 2""")
        items = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(items), 200

    except Exception as e:
        return jsonify(e.messages), 400