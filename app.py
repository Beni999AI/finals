from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import datetime

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = sqlite3.connect("app.db", check_same_thread=False)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("Username is required.")
            return render_template("signup.html")

        if not password:
            flash("Password is required.")
            return render_template("signup.html")

        if password != confirmation:
            flash("Passwords do not match.")
            return render_template("signup.html")

        try:
            db.execute(
                "INSERT INTO users (name, password) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("Username already exists.")
            return render_template("signup.html")

        session["user_id"] = db.execute(
            "SELECT id FROM users WHERE name = ?", (username,)
        ).fetchone()[0]

        return redirect("/")

    return render_template("signup.html")

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    user = db.execute(
        "SELECT name FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    return render_template("index.html", username=user[0])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Username is required.")
            return render_template("login.html")

        if not password:
            flash("Password is required.")
            return render_template("login.html")

        user = db.execute(
            "SELECT id, password FROM users WHERE name = ?", (username,)
        ).fetchone()

        if user is None or not check_password_hash(user[1], password):
            flash("Invalid username or password.")
            return render_template("login.html")

        session["user_id"] = user[0]
        return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        item = request.form.get("item")
        quantity = request.form.get("quantity")
        price = request.form.get("price")
        category = request.form.get("category")
        if not item:
            flash("Item is required.")
            return render_template("add.html")

        if not quantity:
            flash("Quantity is required.")
            return render_template("add.html")

        try:
            db.execute(
                "INSERT INTO products (name, quantity, price, category) VALUES (?, ?, ?, ?)",
                (item, quantity, price, category)
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("Item already exists.")
            return render_template("add.html")

        return redirect("/")

    return render_template("add.html")

@app.route("/stock", methods=["GET", "POST"])
def stock():
    if request.method == "POST":
        item_id = request.form.get("item_id")
        item = request.form.get("item")
        quantity = request.form.get("quantity")
        price = request.form.get("price")
        category = request.form.get("category")
        is_hidden = request.form.get("is_hidden")
        delete_item = request.form.get("is_deleted")
        if item_id:
            query = "UPDATE products SET id = ?"
            params = []
            params.append(item_id)
            if item:
                query += " AND name = ?"
                params.append(item)
            if quantity:
                query += " AND quantity = ?"
                params.append(quantity)
            if price:
                query += " AND price = ?"
                params.append(price)
            if category:
                query += " AND category = ?"
                params.append(category)
            if is_hidden is not None:
                query += " AND is_hidden = 1"
            if delete_item is not None:
                query += " AND is_deleted = 1"

            query += " WHERE id = ?"
            params.append(item_id)
            db.execute(query, tuple(params))
    print(db.execute("SELECT * FROM products").fetchall())
    return render_template("stock.html", items=db.execute("SELECT * FROM products").fetchall())
