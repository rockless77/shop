from app import app, db, User
import sys

def make_user_admin(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"Error: User '{username}' not found.")
            return False
            
        user.is_admin = True
        db.session.commit()
        print(f"Success: User '{username}' is now an admin.")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <username>")
        sys.exit(1)
        
    username = sys.argv[1]
    success = make_user_admin(username)
    sys.exit(0 if success else 1)
