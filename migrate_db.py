import sqlite3
import os
from datetime import datetime

def run_migrations():
    """Run database migrations to add new columns to the User table."""
    print("Starting database migration...")
    
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
        ("first_name", "VARCHAR(100)"),
        ("last_name", "VARCHAR(100)"),
        ("phone_number", "VARCHAR(20)"),
        ("bio", "VARCHAR(500)"),
        ("profile_image", "VARCHAR(255)"),
        ("theme", "VARCHAR(50)"),
        ("language", "VARCHAR(10)"),
        ("timezone", "VARCHAR(50)"),
        ("email_notifications", "BOOLEAN"),
        ("bid_notifications", "BOOLEAN"),
        ("auction_end_notifications", "BOOLEAN"),
        ("order_update_notifications", "BOOLEAN"),
        ("marketing_emails", "BOOLEAN"),
        ("show_email", "BOOLEAN"),
        ("show_phone", "BOOLEAN"),
        ("show_full_name", "BOOLEAN"),
        ("default_address", "VARCHAR(500)"),
        ("default_city", "VARCHAR(100)"),
        ("default_state", "VARCHAR(100)"),
        ("default_zip", "VARCHAR(20)"),
        ("default_country", "VARCHAR(100)"),
        ("default_payment_method", "VARCHAR(100)"),
        ("default_currency", "VARCHAR(3)"),
        ("two_factor_enabled", "BOOLEAN")
    ]
    
    # First add all non-datetime columns
    for column_name, column_type in new_columns:
        if column_name not in existing_columns:
            # For boolean fields, set default to 0 (false)
            if column_type == "BOOLEAN":
                query = f"ALTER TABLE user ADD COLUMN {column_name} {column_type} DEFAULT 0"
            # For varchar fields with defaults
            elif column_name == "theme":
                query = f"ALTER TABLE user ADD COLUMN {column_name} {column_type} DEFAULT 'light'"
            elif column_name == "language":
                query = f"ALTER TABLE user ADD COLUMN {column_name} {column_type} DEFAULT 'en'"
            elif column_name == "timezone":
                query = f"ALTER TABLE user ADD COLUMN {column_name} {column_type} DEFAULT 'UTC'"
            elif column_name == "default_country":
                query = f"ALTER TABLE user ADD COLUMN {column_name} {column_type} DEFAULT 'United States'"
            elif column_name == "default_currency":
                query = f"ALTER TABLE user ADD COLUMN {column_name} {column_type} DEFAULT 'USD'"
            elif column_name == "profile_image":
                query = f"ALTER TABLE user ADD COLUMN {column_name} {column_type} DEFAULT 'default_profile.jpg'"
            else:
                query = f"ALTER TABLE user ADD COLUMN {column_name} {column_type}"
                
            try:
                cursor.execute(query)
                print(f"Added column: {column_name}")
            except sqlite3.OperationalError as e:
                print(f"Error adding column {column_name}: {e}")
    
    # Commit the first batch of changes
    conn.commit()
    
    # Now add the datetime columns
    datetime_columns = [
        ("last_password_change", "DATETIME"),
        ("account_created", "DATETIME"),
        ("last_login", "DATETIME")
    ]
    
    for column_name, column_type in datetime_columns:
        if column_name not in existing_columns:
            query = f"ALTER TABLE user ADD COLUMN {column_name} {column_type}"
            try:
                cursor.execute(query)
                print(f"Added column: {column_name}")
            except sqlite3.OperationalError as e:
                print(f"Error adding column {column_name}: {e}")
    
    # Commit the datetime columns
    conn.commit()
    
    # Now update all existing users to set default values for the new datetime fields
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        cursor.execute("UPDATE user SET last_password_change = ? WHERE last_password_change IS NULL", (now,))
        print("Updated default timestamp for last_password_change")
    except sqlite3.OperationalError as e:
        print(f"Error updating last_password_change: {e}")
        
    try:
        cursor.execute("UPDATE user SET account_created = ? WHERE account_created IS NULL", (now,))
        print("Updated default timestamp for account_created")
    except sqlite3.OperationalError as e:
        print(f"Error updating account_created: {e}")
        
    try:
        cursor.execute("UPDATE user SET last_login = ? WHERE last_login IS NULL", (now,))
        print("Updated default timestamp for last_login")
    except sqlite3.OperationalError as e:
        print(f"Error updating last_login: {e}")
    
    # Final commit and close
    conn.commit()
    conn.close()
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migrations()
