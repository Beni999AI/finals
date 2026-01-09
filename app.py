from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import datetime

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = sqlite3.connect('app.db')


app.route("/signup", methods=["GET", "POST"])
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
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("Username already exists.")
            return render_template("signup.html")

        session["user_id"] = db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()[0]

        return redirect("/")

    return render_template("signup.html")