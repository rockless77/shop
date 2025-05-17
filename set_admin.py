import sqlite3
import os

def make_admin(username):
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'marketplace.db')
    
    # Check if the database exists
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First check if the is_admin column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Add is_admin column if it doesn't exist
        if 'is_admin' not in column_names:
            print("Adding is_admin column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            conn.commit()
        
        # Check if the user exists
        cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"Error: User '{username}' not found.")
            conn.close()
            return False
        
        # Update the user to be an admin
        cursor.execute("UPDATE user SET is_admin = 1 WHERE username = ?", (username,))
        conn.commit()
        
        print(f"Success: User '{username}' is now an admin.")
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python set_admin.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    success = make_admin(username)
    sys.exit(0 if success else 1)
