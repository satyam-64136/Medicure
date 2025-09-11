import sqlite3

# Connect to the database
conn = sqlite3.connect('medicines.db')
cursor = conn.cursor()

# Fetch all rows from the medicines table
cursor.execute('SELECT * FROM medicines')
rows = cursor.fetchall()

# Print column names
cursor.execute("PRAGMA table_info(medicines)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]
print("Columns:", ", ".join(column_names))

# Print all rows
print("\nContents of the 'medicines' table:")
for row in rows:
    print(row)

# Close the connection
conn.close()
