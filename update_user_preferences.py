import sqlite3
import os
from datetime import datetime

def run_migrations():
    """Run database migrations to add new columns to the User table."""
    print("Starting database migration for user preferences...")
    
    db_path = 'instance/marketplace.db'  # Path to the database file
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing columns in the user table
    cursor.execute("PRAGMA table_info(user)")
    existing_columns = [column[1] for column in cursor.fetchall()]
    print(f"Existing columns: {existing_columns}")
    
    # Define the columns we want to add
    new_columns = [
        # Privacy preferences
        {"name": "show_bid_activity", "type": "BOOLEAN", "default": "0"},
        {"name": "show_won_auctions", "type": "BOOLEAN", "default": "0"},
    ]
    
    # Add columns if they don't exist
    columns_added = 0
    for column in new_columns:
        if column["name"] not in existing_columns:
            sql = f"ALTER TABLE user ADD COLUMN {column['name']} {column['type']} DEFAULT {column['default']}"
            try:
                cursor.execute(sql)
                print(f"Added column: {column['name']}")
                columns_added += 1
            except sqlite3.Error as e:
                print(f"Error adding column {column['name']}: {e}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    if columns_added > 0:
        print(f"Successfully added {columns_added} new columns to the user table.")
    else:
        print("No new columns were added. All required columns already exist.")

if __name__ == "__main__":
    run_migrations()
