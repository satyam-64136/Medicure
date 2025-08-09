from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('medicines.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        medicine_name = request.form["medicine_name"].strip()
        conn = get_db_connection()
        # Query the database for the medicine and its alternatives
        medicine = conn.execute("""
            SELECT * FROM medicines
            WHERE generic LIKE ? OR alt1 LIKE ? OR alt2 LIKE ?
        """, (f"%{medicine_name}%", f"%{medicine_name}%", f"%{medicine_name}%")).fetchone()
        conn.close()
        return render_template("results.html", medicine=medicine)
    return render_template("Landing page.html")

if __name__ == "__main__":
    app.run(debug=True)
