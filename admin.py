# admin.py
from werkzeug.security import generate_password_hash
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME"),
)
cursor = conn.cursor()

password = os.getenv("ADMIN_PASS")
if not password:
    raise SystemExit("ADMIN_PASS not set in .env")

password_hash = generate_password_hash(password, method="pbkdf2:sha256")

cursor.execute("""
    INSERT INTO users (username, email, password_hash, role)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash)
""", ("admin", "seyeoyelayo@gmail.com", password_hash, "admin"))

conn.commit()
cursor.close()
conn.close()
print("Admin user created/updated successfully.")
