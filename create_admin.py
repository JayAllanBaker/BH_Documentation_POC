from models import User, db
from app import app

with app.app_context():
    # Check if admin user exists
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", role="admin")
        admin.set_password("password!")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully")
    else:
        # Update existing admin user
        admin.role = "admin"
        admin.set_password("password!")
        db.session.commit()
        print("Admin user updated successfully")
