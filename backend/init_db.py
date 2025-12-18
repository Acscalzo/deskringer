"""
Script to initialize the database and create the first admin user
Run this after deploying to Render or setting up locally
"""

from app import create_app
from models import db, Admin
import sys

def init_database():
    """Initialize database tables"""
    app = create_app()

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")


def create_admin_user(email, password, name):
    """Create an admin user"""
    app = create_app()

    with app.app_context():
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            print(f"✗ Admin user with email {email} already exists!")
            return False

        # Create new admin
        admin = Admin(email=email, name=name)
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print(f"✓ Admin user created successfully!")
        print(f"  Email: {email}")
        print(f"  Name: {name}")
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python init_db.py init              # Initialize database")
        print("  python init_db.py create-admin <email> <password> <name>")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'init':
        init_database()

    elif command == 'create-admin':
        if len(sys.argv) != 5:
            print("Usage: python init_db.py create-admin <email> <password> <name>")
            sys.exit(1)

        email = sys.argv[2]
        password = sys.argv[3]
        name = sys.argv[4]

        create_admin_user(email, password, name)

    else:
        print(f"Unknown command: {command}")
        print("Available commands: init, create-admin")
        sys.exit(1)
