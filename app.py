from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Use a strong, unique secret key in production
app.static_folder = 'static'

# ---------- Database Setup ----------
def setup_medicines_db():
    try:
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
        if c.fetchone()[0] == 0 and os.path.exists("medicine.txt"):
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
    except Exception as e:
        print(f"❌ Error setting up medicines database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def setup_users_db():
    try:
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
    except Exception as e:
        print(f"❌ Error setting up users database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

# ---------- Database Helpers ----------
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
        medicine_name = request.form.get("medicine_name", "").strip()
        if not medicine_name:
            flash("❌ Please enter a medicine name.")
            return redirect(url_for("index"))
        try:
            conn = get_medicines_conn()
            medicine = conn.execute("""
                SELECT * FROM medicines
                WHERE generic LIKE ? OR alt1 LIKE ? OR alt2 LIKE ?
            """, (f"%{medicine_name}%", f"%{medicine_name}%", f"%{medicine_name}%")).fetchone()
            similar_medicines = []
            if medicine:
                similar_medicines = conn.execute("""
                    SELECT * FROM medicines
                    WHERE id != ?
                    ORDER BY RANDOM() LIMIT 3
                """, (medicine['id'],)).fetchall()
            return render_template("results.html", medicine=medicine, similar_medicines=similar_medicines)
        except Exception as e:
            flash(f"❌ Error searching for medicine: {e}")
            return redirect(url_for("index"))
        finally:
            if 'conn' in locals():
                conn.close()
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not email or not password:
            flash("❌ Email and password are required.")
            return redirect(url_for("login"))
        try:
            conn = get_users_conn()
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if user and check_password_hash(user["password"], password):
                session["user_id"] = user["id"]
                session["user_email"] = user["email"]
                flash("✅ Login successful!")
                return redirect(url_for("dashboard"))
            else:
                flash("❌ Invalid email or password.")
                return redirect(url_for("login"))
        except Exception as e:
            flash(f"❌ Error during login: {e}")
            return redirect(url_for("login"))
        finally:
            if 'conn' in locals():
                conn.close()
    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    firstName = request.form.get("firstName", "").strip()
    lastName = request.form.get("lastName", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "")
    confirmPassword = request.form.get("confirmPassword", "")
    if not all([firstName, lastName, email, password, confirmPassword]):
        flash("❌ All fields are required.")
        return redirect(url_for("index"))
    if password != confirmPassword:
        flash("❌ Passwords do not match.")
        return redirect(url_for("index"))
    hashed_pw = generate_password_hash(password)
    try:
        conn = get_users_conn()
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
    except Exception as e:
        flash(f"❌ Error during signup: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("❌ Please log in to access the dashboard.")
        return redirect(url_for("login"))
    try:
        conn = get_users_conn()
        user = conn.execute("SELECT firstName, lastName, email, phone FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        return render_template("dashboard.html", user=user)
    except Exception as e:
        flash(f"❌ Error accessing dashboard: {e}")
        return redirect(url_for("index"))
    finally:
        if 'conn' in locals():
            conn.close()

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_email", None)
    flash("✅ You have been logged out.")
    return redirect(url_for("index"))

@app.route("/users")
def show_users():
    try:
        conn = get_users_conn()
        users = conn.execute("SELECT id, firstName, lastName, email, phone FROM users").fetchall()
        return render_template("users.html", users=users)
    except Exception as e:
        flash(f"❌ Error fetching users: {e}")
        return redirect(url_for("index"))
    finally:
        if 'conn' in locals():
            conn.close()

@app.route("/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        conn = get_users_conn()
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Error deleting user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route("/navbar.html")
def navbar():
    return render_template("navbar.html")

# ---------- Run ----------
if __name__ == "__main__":
    setup_medicines_db()
    setup_users_db()
    app.run(debug=True)
