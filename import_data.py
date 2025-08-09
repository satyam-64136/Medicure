import sqlite3

conn = sqlite3.connect('medicines.db')
c = conn.cursor()

# Create table
c.execute('''
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generic TEXT NOT NULL,
    alt1 TEXT,
    alt2 TEXT
)
''')

# Read medicine.txt and insert
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
conn.close()
print("✅ Data imported successfully!")
 