from app import app, db
import os

def fix_relationships():
    with app.app_context():
        # Get the database file path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Execute SQL to rename the column in the bid table
        db.engine.execute("ALTER TABLE bid RENAME COLUMN user_id TO bidder_id")
        
        print("Relationships fixed successfully!")

if __name__ == "__main__":
    fix_relationships()
