import sqlite3
import os
import datetime

# --- IMPORTANT DATABASE PATH CONFIGURATION ---
# This must be the EXACT ABSOLUTE PATH where your expenses.db will be created.
# It's the same path used in your app.py.
DATABASE = r'C:\Users\Admin\Desktop\MV.clg\personal_expense_tracker\database\expenses.db'

def initialize_database():
    conn = None
    try:
        # Ensure the database directory exists
        db_dir = os.path.dirname(DATABASE)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Create Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name VARCHAR(100) NOT NULL UNIQUE,
                type VARCHAR(10) NOT NULL CHECK (type IN ('Expense', 'Income'))
            );
        """)

        # Create Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date DATE NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('Expense', 'Income')),
                description TEXT,
                category_id INTEGER NOT NULL,
                FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE RESTRICT
            );
        """)

        # Insert Sample Categories (only if they don't exist)
        # This uses INSERT OR IGNORE to prevent errors if run multiple times
        cursor.execute("INSERT OR IGNORE INTO Categories (category_name, type) VALUES ('Food', 'Expense');")
        cursor.execute("INSERT OR IGNORE INTO Categories (category_name, type) VALUES ('Rent', 'Expense');")
        cursor.execute("INSERT OR IGNORE INTO Categories (category_name, type) VALUES ('Salary', 'Income');")
        cursor.execute("INSERT OR IGNORE INTO Categories (category_name, type) VALUES ('Transportation', 'Expense');")
        cursor.execute("INSERT OR IGNORE INTO Categories (category_name, type) VALUES ('Entertainment', 'Expense');")
        cursor.execute("INSERT OR IGNORE INTO Categories (category_name, type) VALUES ('Utilities', 'Expense');")
        cursor.execute("INSERT OR IGNORE INTO Categories (category_name, type) VALUES ('Freelance Income', 'Income');")

        # Get category IDs for sample transactions
        food_id = cursor.execute("SELECT category_id FROM Categories WHERE category_name = 'Food';").fetchone()[0]
        transport_id = cursor.execute("SELECT category_id FROM Categories WHERE category_name = 'Transportation';").fetchone()[0]
        salary_id = cursor.execute("SELECT category_id FROM Categories WHERE category_name = 'Salary';").fetchone()[0]
        entertainment_id = cursor.execute("SELECT category_id FROM Categories WHERE category_name = 'Entertainment';").fetchone()[0]
        freelance_id = cursor.execute("SELECT category_id FROM Categories WHERE category_name = 'Freelance Income';").fetchone()[0]
        rent_id = cursor.execute("SELECT category_id FROM Categories WHERE category_name = 'Rent';").fetchone()[0]
        utilities_id = cursor.execute("SELECT category_id FROM Categories WHERE category_name = 'Utilities';").fetchone()[0]


        # Insert Sample Transactions (using actual dates)
        # Check if Transactions table is empty to avoid duplicate insertions
        if cursor.execute("SELECT COUNT(*) FROM Transactions;").fetchone()[0] == 0:
            today = datetime.date.today()

            cursor.execute("INSERT INTO Transactions (transaction_date, amount, transaction_type, description, category_id) VALUES (?, ?, ?, ?, ?);", (str(today - datetime.timedelta(days=5)), 50.75, 'Expense', 'Groceries', food_id))
            cursor.execute("INSERT INTO Transactions (transaction_date, amount, transaction_type, description, category_id) VALUES (?, ?, ?, ?, ?);", (str(today - datetime.timedelta(days=3)), 15.00, 'Expense', 'Bus fare', transport_id))
            cursor.execute("INSERT INTO Transactions (transaction_date, amount, transaction_type, description, category_id) VALUES (?, ?, ?, ?, ?);", (str(today - datetime.timedelta(days=2)), 1200.00, 'Income', 'Monthly Salary', salary_id))
            cursor.execute("INSERT INTO Transactions (transaction_date, amount, transaction_type, description, category_id) VALUES (?, ?, ?, ?, ?);", (str(today - datetime.timedelta(days=1)), 25.50, 'Expense', 'Movie ticket', entertainment_id))
            cursor.execute("INSERT INTO Transactions (transaction_date, amount, transaction_type, description, category_id) VALUES (?, ?, ?, ?, ?);", (str(today), 8.20, 'Expense', 'Coffee', food_id))
            cursor.execute("INSERT INTO Transactions (transaction_date, amount, transaction_type, description, category_id) VALUES (?, ?, ?, ?, ?);", (str(today), 500.00, 'Income', 'Project payment', freelance_id))
            cursor.execute("INSERT INTO Transactions (transaction_date, amount, transaction_type, description, category_id) VALUES (?, ?, ?, ?, ?);", (str(today - datetime.timedelta(days=35)), 800.00, 'Expense', 'Monthly Rent', rent_id))
            cursor.execute("INSERT INTO Transactions (transaction_date, amount, transaction_type, description, category_id) VALUES (?, ?, ?, ?, ?);", (str(today - datetime.timedelta(days=30)), 150.00, 'Expense', 'Electricity Bill', utilities_id))

        conn.commit()
        print(f"Database initialized successfully at {DATABASE}")

    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    initialize_database()
