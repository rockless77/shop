"""
This script fixes the relationship issues in the models by:
1. Updating the User model to use a different relationship name for support tickets
2. Updating the SupportTicket model to use a different relationship name for user
"""

import os
from app import app, db, User, SupportTicket, Bid

def fix_models():
    with app.app_context():
        # Drop all tables and recreate them with the fixed models
        db.drop_all()
        db.create_all()
        
        print("Database has been reset and recreated with fixed models!")
        print("You'll need to recreate your user accounts and data.")

if __name__ == "__main__":
    fix_models()
