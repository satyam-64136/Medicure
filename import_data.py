import sqlite3
from faker import Faker
from werkzeug.security import generate_password_hash

fake = Faker()

# Connect to users database
conn = sqlite3.connect("users.db")
c = conn.cursor()

for _ in range(10):
    firstName = fake.first_name()
    lastName = fake.last_name()
    email = fake.unique.email()
    phone = fake.phone_number()
    password = generate_password_hash("password123")  # default password for testing

    try:
        c.execute(
            "INSERT INTO users (firstName, lastName, email, phone, password) VALUES (?, ?, ?, ?, ?)",
            (firstName, lastName, email, phone, password)
        )
    except sqlite3.IntegrityError:
        pass  # skip if email already exists

conn.commit()
conn.close()
print("✅ 10 random users added successfully!")
