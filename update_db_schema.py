from app import app, db

def update_user_model():
    with app.app_context():
        # Check if columns already exist
        inspector = db.inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('user')]
        
        # Add new columns if they don't exist
        with db.engine.connect() as conn:
            if 'push_notifications' not in columns:
                conn.execute('ALTER TABLE user ADD COLUMN push_notifications BOOLEAN DEFAULT 1')
            if 'sms_notifications' not in columns:
                conn.execute('ALTER TABLE user ADD COLUMN sms_notifications BOOLEAN DEFAULT 0')
            if 'price_drop_notifications' not in columns:
                conn.execute('ALTER TABLE user ADD COLUMN price_drop_notifications BOOLEAN DEFAULT 1')
            if 'new_listing_notifications' not in columns:
                conn.execute('ALTER TABLE user ADD COLUMN new_listing_notifications BOOLEAN DEFAULT 1')
            if 'email_frequency' not in columns:
                conn.execute('ALTER TABLE user ADD COLUMN email_frequency VARCHAR(20) DEFAULT \'daily\'')
            if 'profile_visibility' not in columns:
                conn.execute('ALTER TABLE user ADD COLUMN profile_visibility VARCHAR(20) DEFAULT \'public\'')
            if 'activity_visibility' not in columns:
                conn.execute('ALTER TABLE user ADD COLUMN activity_visibility VARCHAR(20) DEFAULT \'public\'')
            if 'items_per_page' not in columns:
                conn.execute('ALTER TABLE user ADD COLUMN items_per_page INTEGER DEFAULT 10')
        
        print("Database schema updated successfully!")

if __name__ == "__main__":
    update_user_model()
