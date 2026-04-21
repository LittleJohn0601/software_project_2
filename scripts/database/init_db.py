# init_db.py
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from microblog import app
from blogapp import db

with app.app_context():
    db.create_all()
    print("Database created successfully!")