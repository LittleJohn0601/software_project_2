# add_ban_columns.py
from sqlalchemy import text
from blogapp import create_app, db

app = create_app()

with app.app_context():
    # view user's existing contributes
    inspector = db.inspect(db.engine)
    columns = [c["name"] for c in inspector.get_columns("user")]
    print("Current columns in user table:", columns)

    # add only when it doesn't exist, avoiding being repeated
    if "ban_reason" not in columns:
        db.session.execute(
            text("ALTER TABLE user ADD COLUMN ban_reason VARCHAR(255)")
        )
        print("✅ Added column 'ban_reason'")

    if "ban_until" not in columns:
        db.session.execute(
            text("ALTER TABLE user ADD COLUMN ban_until DATETIME")
        )
        print("✅ Added column 'ban_until'")

    db.session.commit()
    print("✅ Done. Database schema updated.")
