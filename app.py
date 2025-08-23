from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages

# ---------- Medicines Database ----------
def setup_medicines_db():
    conn = sqlite3.connect('medicines.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        generic TEXT NOT NULL,
        alt1 TEXT,
        alt2 TEXT,
        price REAL DEFAULT 0,
        alt1_price REAL DEFAULT 0,
        alt2_price REAL DEFAULT 0
    )
    ''')

    c.execute("SELECT COUNT(*) FROM medicines")
    if c.fetchone()[0] == 0:
        if os.path.exists("medicine.txt"):
            with open('medicine.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = [p.strip() for p in line.split('/')]
                        if len(parts) >= 3:
                            generic, alt1, alt2 = parts[0], parts[1], parts[2]
                            c.execute(
                                "INSERT INTO medicines (generic, alt1, alt2) VALUES (?, ?, ?)",
                                (generic, alt1, alt2)
                            )
            conn.commit()
            print("✅ Medicines imported successfully!")
    conn.close()

# ---------- Users Database ----------
def setup_users_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstName TEXT NOT NULL,
        lastName TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# ---------- DB Helpers ----------
def get_medicines_conn():
    conn = sqlite3.connect('medicines.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_users_conn():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        medicine_name = request.form["medicine_name"].strip()
        conn = get_medicines_conn()

        # Fetch main medicine
        medicine = conn.execute("""
            SELECT * FROM medicines
            WHERE generic LIKE ? OR alt1 LIKE ? OR alt2 LIKE ?
        """, (f"%{medicine_name}%", f"%{medicine_name}%", f"%{medicine_name}%")).fetchone()

        # Fetch 3 random similar medicines excluding the main one
        similar_medicines = []
        if medicine:
            similar_medicines = conn.execute("""
                SELECT * FROM medicines
                WHERE id != ?
                ORDER BY RANDOM() LIMIT 3
            """, (medicine['id'],)).fetchall()

        conn.close()
        return render_template("results.html", medicine=medicine, similar_medicines=similar_medicines)

    # GET request → render homepage
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    firstName = request.form["firstName"].strip()
    lastName = request.form["lastName"].strip()
    email = request.form["email"].strip()
    phone = request.form["phone"].strip()
    password = request.form["password"]
    confirmPassword = request.form["confirmPassword"]

    if password != confirmPassword:
        flash("❌ Passwords do not match.")
        return redirect(url_for("index"))

    hashed_pw = generate_password_hash(password)

    conn = get_users_conn()
    try:
        conn.execute(
            "INSERT INTO users (firstName, lastName, email, phone, password) VALUES (?, ?, ?, ?, ?)",
            (firstName, lastName, email, phone, hashed_pw)
        )
        conn.commit()
        flash("✅ Account created successfully! Please log in.")
        print(f"🟢 New user created: {firstName} {lastName}, Email: {email}")
    except sqlite3.IntegrityError:
        flash("⚠️ Email already exists. Try logging in.")
        print(f"⚠️ Signup failed. Email already exists: {email}")
    finally:
        conn.close()

    return redirect(url_for("index"))

@app.route("/users")
def show_users():
    """Admin page to view all registered users"""
    conn = get_users_conn()
    users = conn.execute("SELECT id, firstName, lastName, email, phone FROM users").fetchall()
    conn.close()
    return render_template("users.html", users=users)

# ---------- Delete User AJAX ----------
@app.route("/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        conn = get_users_conn()
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True}), 200
    except Exception as e:
        print("Error deleting user:", e)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/navbar.html")
def navbar():
    return render_template("navbar.html")

# ---------- Run ----------
if __name__ == "__main__":
    setup_medicines_db()
    setup_users_db()
    app.run(debug=True)
