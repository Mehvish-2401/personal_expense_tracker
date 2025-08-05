import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_super_secret_key' # Needed for flash messages

# Define the path to your database file
# IMPORTANT: Make sure this path is correct relative to app.py
# app.py and 'database' folder should be in the same parent folder
DATABASE = 'database/expenses.db'

# --- Database Helper Functions ---
# Function to get a database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Configure connection to return rows as dictionaries (or sqlite3.Row objects),
        # which makes accessing columns by name easier (e.g., row['column_name'])
        db.row_factory = sqlite3.Row
    return db

# Function to close the database connection when the application context ends
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Generic function to execute a query and fetch results
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# --- Routes (Web Pages/API Endpoints) ---

# Main page: Displays transactions and summary, and provides a form to add new transactions
@app.route('/')
def index():
    # Get current month's start and end dates
    today = datetime.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # End of month is tricky, so we'll just query until the current date for simplicity or adjust query
    # For full month summary regardless of current date, you'd get the last day of the month
    # For now, let's keep it simple and query for the current month's transactions.
    # SQLite's date functions are 'YYYY-MM-DD'

    # Retrieve all transactions with their category names using a JOIN
    transactions = query_db("""
        SELECT T.transaction_id, T.transaction_date, T.amount, T.transaction_type, T.description, C.category_name, C.type as category_type
        FROM Transactions T
        JOIN Categories C ON T.category_id = C.category_id
        WHERE STRFTIME('%Y-%m', T.transaction_date) = STRFTIME('%Y-%m', CURRENT_DATE)
        ORDER BY T.transaction_date DESC, T.transaction_id DESC;
    """)

    # Calculate monthly income and expenses
    monthly_income = query_db("""
        SELECT SUM(amount) FROM Transactions
        WHERE transaction_type = 'Income' AND STRFTIME('%Y-%m', transaction_date) = STRFTIME('%Y-%m', CURRENT_DATE);
    """, one=True)[0] or 0.0

    monthly_expenses = query_db("""
        SELECT SUM(amount) FROM Transactions
        WHERE transaction_type = 'Expense' AND STRFTIME('%Y-%m', transaction_date) = STRFTIME('%Y-%m', CURRENT_DATE);
    """, one=True)[0] or 0.0

    net_balance = monthly_income - monthly_expenses

    # Retrieve all categories for the form dropdown
    categories = query_db("SELECT * FROM Categories ORDER BY category_name;")

    return render_template('index.html',
                           transactions=transactions,
                           monthly_income=monthly_income,
                           monthly_expenses=monthly_expenses,
                           net_balance=net_balance,
                           categories=categories,
                           now=datetime.now)

# Route to add a new transaction
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if request.method == 'POST':
        transaction_date = request.form['transaction_date']
        amount = float(request.form['amount'])
        transaction_type = request.form['transaction_type']
        category_id = request.form['category_id']
        description = request.form['description']

        db = get_db()
        db.execute("INSERT INTO Transactions (transaction_date, amount, transaction_type, category_id, description) VALUES (?, ?, ?, ?, ?);",
                   (transaction_date, amount, transaction_type, category_id, description))
        db.commit()
        # Changed flash category for confetti trigger
        flash('Transaction added successfully!', 'success-confetti')
        return redirect(url_for('index'))

# Route to delete a transaction
@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    db = get_db()
    db.execute("DELETE FROM Transactions WHERE transaction_id = ?;", (transaction_id,))
    db.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('index'))

# Route to display and add categories
@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category_name = request.form['category_name'].strip()
        category_type = request.form['category_type']

        if not category_name:
            flash('Category name cannot be empty!', 'error')
            return redirect(url_for('add_category'))

        db = get_db()
        try:
            db.execute("INSERT INTO Categories (category_name, type) VALUES (?, ?);", (category_name, category_type))
            db.commit()
            flash(f'Category "{category_name}" added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash(f'Category "{category_name}" already exists!', 'error')
        return redirect(url_for('add_category'))

    categories = query_db("SELECT * FROM Categories ORDER BY category_name;")
    return render_template('add_category.html', categories=categories)


if __name__ == '__main__':
    app.run(debug=True)