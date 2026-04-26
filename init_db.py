"""
Run this ONCE after deploying to Railway to set up the database.
Command: python init_db.py
"""
from dotenv import load_dotenv
load_dotenv()
from database import init_db
print("Setting up PostgreSQL database...")
init_db()
print("Done! Database ready.")
