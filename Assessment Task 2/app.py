from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = "my_task_app_secret_key"

DATABASE = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("home"))
        return function(*args, **kwargs)

    return wrapper

@app.route("/", methods=["GET", "POST"])
def home():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "admin" and password == "1234":
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("tasks"))

        error = "Invalid username or password!"

    return render_template("login.html", error=error)

@app.route("/tasks", methods=["GET"])
@login_required
def tasks():
    conn = get_db_connection()
    task_list = conn.execute(
        "SELECT id, title, status FROM tasks ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("tasks.html", tasks=task_list)

@app.route("/add_task", methods=["POST"])
@login_required
def add_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()

    if not title:
        return jsonify({
            "success": False,
            "message": "Task title cannot be empty!"
        }), 400

    conn = get_db_connection()

    cursor = conn.execute(
        "INSERT INTO tasks (title) VALUES (?)",
        (title,)
    )

    task_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Task added successfully!",
        "task": {
            "id": task_id,
            "title": title,
            "status": "Pending"
        }
    }), 201

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
