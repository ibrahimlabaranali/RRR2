import sqlite3

conn = sqlite3.connect('your_database.db')  # Use your actual database file
c = conn.cursor()

# Add nin column if it doesn't exist
try:
    c.execute("ALTER TABLE users ADD COLUMN nin TEXT;")
    print("Column 'nin' added.")
except sqlite3.OperationalError:
    print("Column 'nin' already exists.")

conn.commit()
conn.close()