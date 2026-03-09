# We first need to import the mysql connector
# https://www.w3schools.com/python/python_mysql_getstarted.asp

import mysql.connector

#After that we need to have our database connected

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Malaz122",
    database="supplier_inventory"
)


# Now we need to have a cursor and it's better to have a variable for that
# instead of making a new db.cursor everytime
# https://www.w3schools.com/python/python_mysql_insert.asp
mycursor = mydb.cursor()

def view_suppliers():
    # We select all the records from the table called "Supplier".
    mycursor.execute("SELECT * FROM Supplier")
    # Here we get all the rows so we can start working and reading them easily.
    rows = mycursor.fetchall()
    
    # Now we need to make check so we avoid any errors, so we check if rows are 0 and return an error.
    if len(rows) == 0:
        print("No current suppliers in the database")
        return
    
    # If there are suppliers then we loop through them and return everything.
    print("\ ------ SUPPLIERS ------")
    for row in rows:
        # id, name, contact and address.
            print(" " + str(row[0]) + " - " + str(row[1]) + " - " + str(row[2]) + " - " + str(row[3]))


def add_supplier():
    name = input("Supplier name: ")
    contact = input("Contact info: ")
    address = input("Address (optional): ")
    
    # Because the address are optional, then we need to check if it's empty to send a static one.
    if address == "":
        address = None
    
    # Remember the procedure we created, now we make use of it and send our variables.
    # https://python-oracledb.readthedocs.io/en/latest/user_guide/plsql_execution.html
    mycursor.callproc('new_supplier', (name, contact, address))
    
    # https://www.geeksforgeeks.org/python/commit-rollback-operation-in-python/
    mydb.commit()
    print ("Added " + name + " to our suppliers list!")
    

def remove_supplier():
    view_suppliers()
    
    # We ask for the supplier id
    supplier_id = input("\nProvide the supplier ID to remove it: ")
    
    # Remember when we choosed %s now we make use of it and replace it by our supplier id.
    # I didn't know about the "," at the end but found that execute handled as tuple.
    mycursor.execute("DELETE FROM Purchase WHERE supplier_id = %s", (supplier_id,))
    mycursor.execute("DELETE FROM Supplier WHERE supplier_id = %s", (supplier_id,))

    mydb.commit()
    
    # Now we check if there were any suppliers rows that got deleted (NEED A BETTER CODE)
    if mycursor.rowcount > 0:
        print("Supplier deleted.")
    else:
        print("Could not find the supplier")
        

def view_products():
    # Now we need to show our products from the product table:
    mycursor.execute("SELECT * FROM Product")
    
    # Check if we have rows for products or not
    rows = mycursor.fetchall()
    if len(rows) == 0:
        print("There are no products found.")
        return
    
    print("\n ----- PRODUCTS -----")
    for row in rows:
        # Same as we did in suppliers
        print(" " + str(row[0]) + " - " + str(row[1]) + " - " + str(row[2]) + " - " + str(row[3]))


def add_product():
    name = input("Type the product name you want to add: ")
    
    print ("Pick a category from the list below: ")
    print (" Food = 1")
    print (" Drinks = 2")
    print (" Chemicals = 3")
    # Took help with categories names from AI
    
    answer = input("Your category choice: ")
    
    if answer == "1":
        category = "food"
    elif answer == "2":
        category = "Drinks"
    elif answer == "3":
        category = "Chemicals"
    else:
        print("Not a valid category number.")
        return
    
    # Because each unit have a weight and we need to know the weight for it.
    unit = input("What are the unit in kg? ")
    
    # https://www.w3schools.com/python/python_mysql_insert.asp
    sql = "INSERT INTO Product (name, category, unit) VALUES (%s, %s, %s)"
    mycursor.execute(sql, (name, category, unit))
    mydb.commit()
    
    
    # After we added the product to our Product table, we need to also change the stock table.
    # So we don't break other functions.
    new_id = mycursor.lastrowid # This way we get the product id we inserted instead of searching again.
    mycursor.execute("INSERT INTO Stock (product_id, quantity, last_updated) VALUES (%s, 0, CURDATE())", (new_id,))
    mydb.commit()
    print("Product added. Change the stock based on your needs.")


def remove_product():
    view_products()
    product_id = input(" Give us the product id you want to remove.")
    
    # So we don't hit an error with the foreign key, we need to delete it 
    # from other tables first.. learned this the hard way :9
    mycursor.execute("DELETE FROM PriceHistory WHERE product_id = %s", (product_id,))
    mycursor.execute("DELETE FROM Stock WHERE product_id = %s", (product_id,))
    mycursor.execute("DELETE FROM Purchase WHERE product_id = %s", (product_id,))
    mycursor.execute("DELETE FROM Product WHERE product_id = %s", (product_id,))
    mydb.commit()
    
    if mycursor.rowcount > 0:
        print("Product deleted!")
    else:
        print("Can't find that product, please try again.")

def new_purchase():
    print("Add a new stock")
    
    view_suppliers()
    supplier_id = input("Supplier ID: ")
    view_products()
    product_id = input("Product ID: ")
    
    quantity = input("How many? ")
    total_cost = input("Total cost? ")
    date = input("Date (YYYY-MM-DD)? ")
    
    # Now we need to send it to the database and insert it:
    # https://www.w3schools.com/python/python_mysql_insert.asp
    sql = "INSERT INTO Purchase (supplier_id, product_id, quantity, purchase_date, total_amount) VALUES (%s, %s, %s, %s, %s)"
    mycursor.execute(sql, (supplier_id, product_id, quantity, date, total_cost))
    mydb.commit()
    
    print("Stock has been updated!")


def purchase_history():
    # Here we join both purchase and supplier product to get the name.
    # This is the query we had in our plan
    sql = """
SELECT Purchase.purchase_id, Supplier.name, Product.name, Purchase.quantity, Purchase.purchase_date, Purchase.total_amount
FROM Purchase
INNER JOIN Supplier ON Purchase.supplier_id = Supplier.supplier_id
INNER JOIN Product ON Purchase.product_id = Product.product_id
ORDER BY Purchase.purchase_date DESC
"""
    mycursor.execute(sql)
    rows = mycursor.fetchall()
    
    if len(rows) == 0:
        print("No purchases yet.")
        return

    print("----- PURCHASE HISTORY -----")
    for row in rows:
        print("  ID: " + str(row[0]) + " - " + row[1] + " bought " + row[2] + " - amount: " + str(row[3]) + " - sum: " + str(row[5]) + " usd")


def our_stock():
    # We select our products rows to them after that.
    sql = "SELECT Product.name, Product.category, Stock.quantity, Stock.last_updated FROM Stock INNER JOIN Product ON Stock.product_id = Product.product_id ORDER BY Stock.quantity ASC"
    mycursor.execute(sql)
    rows = mycursor.fetchall()
    
    if len(rows) == 0:
        print("Your stock are empty.")
        return
        
    print("----- Stock levels -----")
    for level in rows:
        # printing the name, category, quantity, and date
        print(f"  {level[0]} ({level[1]}) - {level[2]} in stock. DATE {level[3]}")


def spending_per_supplier():
    # Here we use the sum query we talked about in the plan (query 3)
    sql = "SELECT Supplier.name, SUM(Purchase.total_amount) as total FROM Purchase JOIN Supplier ON Purchase.supplier_id = Supplier.supplier_id GROUP BY Supplier.name ORDER BY total DESC"
    mycursor.execute(sql)
    rows = mycursor.fetchall()

    # If there were no rows then there are no data
    if len(rows) == 0:
        print("Found nothing!")
    else:
        print("----- Total spent per supplier -----")
        for each in rows:
            # supplier and total bill
            print(f"  {each[0]}: {each[1]} kr")



# Now we start with our CLI:
def main():
    print("Supplier Inventory System")
    print("--------------------------------")
    
    # A while loop
    while True:
        print("Select one from the options below!")
        print("1. View suppliers")
        print("2. Add supplier")
        print("3. Remove supplier")
        print("4. View products")
        print("5. Add product")
        print("6. Remove product") 
        print("7. New stock")
        print("8. Purchase history")
        print("9. Check the stock")
        print("10. Spending per supplier")
        print("q. Quit")
    
        choice = input("Choice: ")
    
        # Now based on the choice we call the right function.
        
        if choice == '1':
            view_suppliers()
        elif choice == '2':
            add_supplier()
        elif choice == '3':
            remove_supplier()
        elif choice == '4':
            view_products()
        elif choice == "5":
            add_product()
        elif choice == "6":
            remove_product()
        elif choice == "7":
            new_purchase()
        elif choice == "8":
            purchase_history()
        elif choice == "9":
            our_stock()
        elif choice == "10":
            spending_per_supplier()
        elif choice == "q":
            print("bye!")
            break
        else:
            print("not a valid option, try again")


# The main function won't call itself:
main()

# We don't need to forget to clean and save our connection. 
mycursor.close()
mydb.close()