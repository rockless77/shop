import sqlite3
import os
from datetime import datetime

def run_migrations():
    """Run database migrations to add new columns to the User table and create new tables."""
    print("Starting database migration for user preferences and security features...")
    
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
    print(f"Existing columns in user table: {len(existing_columns)}")
    
    # Define the columns we want to add to the User table
    new_columns = [
        # Shipping Preferences
        {"name": "preferred_shipping_method", "type": "TEXT", "default": "'standard'"},
        {"name": "shipping_notifications", "type": "BOOLEAN", "default": "1"},
        {"name": "signature_required", "type": "BOOLEAN", "default": "0"},
        {"name": "show_delivery_instructions", "type": "BOOLEAN", "default": "1"},
        
        # Account Recovery
        {"name": "recovery_email", "type": "TEXT", "default": "NULL"},
        {"name": "recovery_phone", "type": "TEXT", "default": "NULL"},
        {"name": "security_question1", "type": "TEXT", "default": "NULL"},
        {"name": "security_answer1", "type": "TEXT", "default": "NULL"},
        {"name": "security_question2", "type": "TEXT", "default": "NULL"},
        {"name": "security_answer2", "type": "TEXT", "default": "NULL"},
    ]
    
    # Add columns to User table if they don't exist
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
    
    # Check if the payment_method table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payment_method'")
    if not cursor.fetchone():
        print("Creating payment_method table...")
        cursor.execute('''
        CREATE TABLE payment_method (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            payment_type TEXT NOT NULL,
            is_default BOOLEAN DEFAULT 0,
            nickname TEXT,
            last_four TEXT,
            expiry_month INTEGER,
            expiry_year INTEGER,
            card_brand TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
        ''')
        print("Created payment_method table")
    
    # Check if the shipping_address table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shipping_address'")
    if not cursor.fetchone():
        print("Creating shipping_address table...")
        cursor.execute('''
        CREATE TABLE shipping_address (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nickname TEXT,
            recipient_name TEXT NOT NULL,
            street_address1 TEXT NOT NULL,
            street_address2 TEXT,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            postal_code TEXT NOT NULL,
            country TEXT NOT NULL,
            phone_number TEXT,
            is_default BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
        ''')
        print("Created shipping_address table")
    
    # Check if the login_history table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='login_history'")
    if not cursor.fetchone():
        print("Creating login_history table...")
        cursor.execute('''
        CREATE TABLE login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            location TEXT,
            success BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
        ''')
        print("Created login_history table")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Successfully added {columns_added} new columns to the user table and created necessary tables.")
    print("Database migration completed successfully!")

if __name__ == "__main__":
    run_migrations()
