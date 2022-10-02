import requests

"""
The table "product_items" in db1 contains items with the following fields (see db1/db_init.sql):
    id SERIAL PRIMARY KEY,
    product_id integer NOT NULL,
    name varchar(1000) NOT NULL,
    price numeric NOT NULL

This method clones all items of one product and apply a coefficien to their prices.
    @param product_id (int) - source product id
    @param new_product_id (int) - target product id
    @param coef (double): price multiplicator

Communication with the database is processed via the ms1

Return the number of clonned items
"""
def clone_product(product_id, new_product_id, coef):
    LIST_PRODUCT_URL = "http://ms1:8000/product_items"
    items = requests.get(url = f"{LIST_PRODUCT_URL}/{product_id}").json()
    
    ADD_PRODUCT_URL = "http://ms1:8000/product_item"
    for item in items:
        del(item['id'])
        item['product_id'] = new_product_id
        item['price'] *= coef
        requests.put(url = ADD_PRODUCT_URL, json = item)

    return len(items)

"""
Find the sum of items prices of a product
"""
def sum_of_prices(product_id):
    LIST_PRODUCT_URL = "http://ms1:8000/product_items"
    items = requests.get(url = f"{LIST_PRODUCT_URL}/{product_id}").json()
    
    return round(sum([i['price'] for i in items]))


"""
Delete all product's items
"""
def delete_product(product_id):
    LIST_PRODUCT_URL = "http://ms1:8000/product"
    
    return requests.delete(url = f"{LIST_PRODUCT_URL}/{product_id}").text
