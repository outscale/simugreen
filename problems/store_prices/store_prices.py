import psycopg2

def update_prices(product_ids, coef):
    """This methods receive a list of product whose price have changed
    and a change coeficient. 
    It aims to update their price in the store database."""
    new_prices =  []
    for product_id in product_ids:

        # Instanciate a connection to the postgre db
        connection = psycopg2.connect(user="hackaton",
                                  password="super_secret",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="postgres_db")
        
        select_query = f"SELECT price FROM products WHERE product_id = {product_id}"
        cursor = connection.cursor()
        cursor.execute(select_query)
        
        product_price = cursor.fetchone() # Select price of the product with the corresponding id from db
        new_price = product_price * coef

        update_query = f"UPDATE products SET price = %s WHERE product_id = %s"

        # Execute the update query and close connection client
        cursor.execute(update_query, (new_price, product_id))
        connection.commit()
        cursor.close()
        connection.close()

        new_prices.append(new_price)
    
    return new_prices

