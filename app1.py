from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(
    __name__,
    template_folder="Expense-Tracker-Website/templates",
    static_folder="Expense-Tracker-Website/static",
)

DATABASE = "expenses.db"


# Connect to database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create expenses table
def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            expense_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Home page
@app.route("/")
def home():
    conn = get_db_connection()

    search = request.args.get("search", "")

    if search:
        expenses = conn.execute("""
            SELECT * FROM expenses
            WHERE title LIKE ?
            OR category LIKE ?
            ORDER BY expense_date DESC
        """, (f"%{search}%", f"%{search}%")).fetchall()
    else:
        expenses = conn.execute("""
            SELECT * FROM expenses
            ORDER BY expense_date DESC
        """).fetchall()

    total = conn.execute(
        "SELECT SUM(amount) FROM expenses"
    ).fetchone()[0]

    count = conn.execute(
        "SELECT COUNT(*) FROM expenses"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total or 0,
        count=count,
        search=search,
        today=date.today().isoformat()
    )


# Add expense
@app.route("/add", methods=["POST"])
def add_expense():
    title = request.form["title"]
    amount = request.form["amount"]
    category = request.form["category"]
    expense_date = request.form["expense_date"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO expenses (title, amount, category, expense_date)
        VALUES (?, ?, ?, ?)
    """, (title, amount, category, expense_date))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# Delete expense
@app.route("/delete/<int:id>")
def delete_expense(id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM expenses WHERE id = ?", (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    create_table()
    app.run(debug=True, port=5001)
