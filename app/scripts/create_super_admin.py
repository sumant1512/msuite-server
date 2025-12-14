from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.enums.user_role import UserRole
from app.core.security import get_password_hash

def create_super_admin():
    db: Session = SessionLocal()

    exists = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
    if exists:
        print("❌ Super Admin already exists")
        return

    admin = User(
        name="Super Admin",
        email="admin@msuite.com",
        password_hash=get_password_hash("admin"),
        role=UserRole.SUPER_ADMIN
    )

    db.add(admin)
    db.commit()
    print("✅ Super Admin created")

if __name__ == "__main__":
    create_super_admin()
