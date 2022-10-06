import psycopg2
from flask import Flask, jsonify, request

# See README.md for details

# Don't forget to relaod the service after any code change: 
#   ./ms1_connect.sh
#   sudo systemctl restart ms1.service
# 
# To see the errors:
#   ./ms1_connect.sh
#   journalctl -u ms1.service

HOST = "db1"
DATABASE = "postgres"
USERNAME = "postgres"
PASSWORD = "postgres"

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Welcome to the hackaton app!</p>"


"""
The table "products" in db1 contains items with the following fields (see db1/db_init.sql):
    id SERIAL PRIMARY KEY,
    product_id integer NOT NULL,
    name varchar(1000) NOT NULL,
    price numeric NOT NULL
This method list its items filtered by product_id
Request parameters:
    product_id
Return: List of product items

To test the method:
    curl -i -X GET http://<ms1-ip>:8000/product_items/1
"""
@app.route('/product_items/<product_id>')
def product_items(product_id):
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=HOST,
            database=DATABASE,
            user=USERNAME,
            password=PASSWORD)

        cur = conn.cursor()

        cur.execute(f"""SELECT * FROM product_items WHERE product_id={product_id}""")
        items = cur.fetchall()
        # convert arrays into objects
        items = [{"id":i[0], "product_id": i[1], "name": i[2], "price": i[3] } for i in items]

        return jsonify(items), 200

    except Exception as e:
        return jsonify(e.messages), 400

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()     


"""
Add new item into "product_items" table.
Request paramaters:
    - id 
    - product_id
    - name
    - price

To test the method:
    curl -i -H "Content-Type: application/json" -X PUT -d '{"id":1000, "product_id":100, "name":"some name", "price":11}' \
        http://<ms1-ip>:8000/product_item
"""
@app.route('/product_item', methods=['PUT'])
def add_product_item():
    params = request.json
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=HOST,
            database=DATABASE,
            user=USERNAME,
            password=PASSWORD)

        cur = conn.cursor()

        cur.execute(f"""INSERT INTO product_items (product_id, name, price) VALUES 
            ({params['product_id']}, '{params['name']}', {params['price']})""")
        conn.commit()

        return "The product items was successefully added", 200

    except Exception as e:
        return jsonify(e.messages), 400

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


"""
Delete items for a product from "product_items" table.
Request paramaters:
    - product_id

To test the method:
    curl -i -X DELETE http://<ms1-ip>:8000/product/100
"""
@app.route('/product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=HOST,
            database=DATABASE,
            user=USERNAME,
            password=PASSWORD)

        cur = conn.cursor()

        cur.execute(f"""DELETE FROM product_items WHERE product_id = {product_id}""")
        conn.commit()

        return f"Product {product_id} was successefully deleted", 200

    except Exception as e:
        return jsonify(e.messages), 400

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
