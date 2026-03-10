# init_db.py
from microblog import app
from blogapp import db

with app.app_context():
    db.create_all()
    print("Database created successfully!")