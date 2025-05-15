from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    print("Tables in database:", inspector.get_table_names())
    if 'support_ticket' in inspector.get_table_names():
        print("\nSupport ticket table columns:")
        for column in inspector.get_columns('support_ticket'):
            print(f"- {column['name']} ({column['type']})")
    else:
        print("\nSupport ticket table does not exist")
