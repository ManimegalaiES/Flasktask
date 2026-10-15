from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "dev-only-change-this-secret-key"
)

DATABASE = os.path.join(app.root_path, "users.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    return redirect(url_for("register"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password", ""
        )

        if not all([name, email, phone, password, confirm_password]):
            flash("Please fill in all the fields.", "error")
            return render_template("register.html")

        if len(name) > 100 or len(email) > 254 or len(phone) > 20:
            flash("One or more fields are too long.", "error")
            return render_template("register.html")

        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            flash("Please enter a valid email address.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()

        try:
            conn.execute(
                """
                INSERT INTO users (name, email, phone, password)
                VALUES (?, ?, ?, ?)
                """,
                (name, email, phone, hashed_password)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            flash("This email is already registered.", "error")
            return render_template("register.html")

        finally:
            conn.close()

        return redirect(url_for("success"))

    return render_template("register.html")

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to view your details.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()

    user = conn.execute(
        """
        SELECT id, name, email, phone
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    if user is None:
        session.clear()
        flash("User account not found. Please log in again.", "error")
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out successfully.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
