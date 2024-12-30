from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Функція для підключення до бази даних
def connect_to_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="1233",  # Замініть на ваш пароль
        database="sql_kursova"  # Замініть на вашу базу даних
    )

# Головна сторінка
@app.route("/")
def index():
    return render_template("index.html")

# Каталог товарів
@app.route("/catalog")
def catalog():
    db = connect_to_database()
    with db.cursor() as cursor:
        cursor.execute(""" 
            SELECT p.id, p.product_name, p.price, a.total_amount 
            FROM products p
            LEFT JOIN availability a ON p.id = a.product_id
        """)
        products = cursor.fetchall()
    db.close()
    return render_template("catalog.html", products=products)

cart = []

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    quantity = int(request.form["quantity"])
    db = connect_to_database()
    with db.cursor() as cursor:
        cursor.execute("SELECT id, product_name, price FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if product:
            # Перевіряємо, чи товар вже є в кошику
            for item in cart:
                if item["id"] == product[0]:
                    item["quantity"] += quantity
                    break
            else:
                cart.append({
                    "id": product[0],
                    "name": product[1],
                    "price": product[2],
                    "quantity": quantity
                })
            flash("Товар успішно додано до кошика!")
        else:
            flash("Товар не знайдено!")
    db.close()
    return redirect(url_for("catalog"))

@app.route("/order_history")
def order_history():
    # Логіка для відображення історії замовлень
    return render_template("order_history.html")

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        customer_name = request.form["customer_name"]
        customer_email = request.form["customer_email"]

        db = connect_to_database()
        with db.cursor() as cursor:
            for item in cart:
                cursor.execute("""
                    INSERT INTO orders (product_id, customers_id, total_price, total_amount, order_date, order_status)
                    VALUES (%s, %s, %s, %s, NOW(), %s)
                """, (item["id"], 1, item["price"] * item["quantity"], item["quantity"], True))
        db.commit()
        db.close()

        cart.clear()
        flash("Замовлення успішно оформлено!")
        return redirect(url_for("index"))

    total_price = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("checkout.html", cart=cart, total_price=total_price)

@app.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    global cart
    cart = [item for item in cart if item["id"] != product_id]
    flash("Товар успішно видалено з кошика!")
    return redirect(url_for("view_cart"))


@app.route("/cart")
def view_cart():
    total_price = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("cart.html", cart=cart, total_price=total_price)

if __name__ == "__main__":
    app.run(debug=True)
