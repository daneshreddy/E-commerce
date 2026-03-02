from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.secret_key = "Danesh@0406"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        image TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        total REAL,
        payment_method TEXT,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        product_id INTEGER,
        quantity INTEGER DEFAULT 1,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    conn.commit()
    conn.close()


@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return render_template('index.html', username=session['username'], products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid Username or Password")

    return render_template('login.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == "POST":
        username = request.form['username']
        new_password = generate_password_hash(request.form['password'])

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user:
            cursor.execute("UPDATE users SET password=? WHERE username=?",
                           (new_password, username))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        else:
            conn.close()
            return render_template("forgot.html", error="User not found")

    return render_template("forgot.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username or Email already exists")

    return render_template("register.html")

@app.route('/load_products')
def load_products():

    response = requests.get("https://fakestoreapi.com/products/category/electronics")
    data = response.json()

    conn = get_connection()
    cursor = conn.cursor()

    for item in data:
        cursor.execute(
            "INSERT OR IGNORE INTO products (name, price, description, image) VALUES (?, ?, ?, ?)",
            (item['title'], item['price'], item['description'], item['image'])
        )

    conn.commit()
    conn.close()

    return "Products Loaded Successfully"

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT quantity FROM cart
        WHERE username=? AND product_id=?
    """, (session['username'], product_id))

    item = cursor.fetchone()

    if item:
        cursor.execute("""
            UPDATE cart
            SET quantity = quantity + 1
            WHERE username=? AND product_id=?
        """, (session['username'], product_id))
    else:
        cursor.execute("""
            INSERT INTO cart (username, product_id, quantity)
            VALUES (?, ?, 1)
        """, (session['username'], product_id))

    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/remove/<int:product_id>')
def remove(product_id):

    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM cart WHERE username=? AND product_id=?",
        (session['username'], product_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT products.id,
               products.name,
               products.price,
               products.image,
               cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.username=?
    """, (session['username'],))

    items = cursor.fetchall()
    total = sum(item[2] * item[4] for item in items)

    conn.close()

    return render_template('cart.html', items=items, total=total)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        session['address'] = request.form
        return redirect(url_for('payment'))

    return render_template('address.html')


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        payment_method = request.form['payment']

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT products.id,
                   products.price,
                   cart.quantity
            FROM cart
            JOIN products ON cart.product_id = products.id
            WHERE cart.username=?
        """, (session['username'],))

        items = cursor.fetchall()
        total = sum(item[1] * item[2] for item in items)

        cursor.execute("""
            INSERT INTO orders (username, total, payment_method)
            VALUES (?, ?, ?)
        """, (session['username'], total, payment_method))

        order_id = cursor.lastrowid

        for item in items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity)
                VALUES (?, ?, ?)
            """, (order_id, item[0], item[2]))

        cursor.execute("DELETE FROM cart WHERE username=?", (session['username'],))

        conn.commit()
        conn.close()

        return render_template("success.html", total=total)

    return render_template("payment.html")


if __name__ == '__main__':
    init_db()
    app.run(debug=True)