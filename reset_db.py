from app import app, db
import os

def reset_database():
    with app.app_context():
        # Get the database file path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        print("Database has been reset successfully!")

if __name__ == "__main__":
    reset_database()
