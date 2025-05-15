from app import app, db
import os

def reset_and_fix_database():
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        print("Database has been reset and recreated with the fixed schema!")

if __name__ == "__main__":
    reset_and_fix_database()
