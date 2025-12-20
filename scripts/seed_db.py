"""
Database seeding script to initialize the database with a Super Admin user.

This script creates an initial SUPER_ADMIN user with predefined credentials.
Run this after setting up the database and running migrations.

Usage:
    poetry run python scripts/seed_db.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.enums.user_role import UserRole


def seed_database():
    """Create initial Super Admin user."""
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL, echo=False)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Check if any super admin already exists
        existing_admin = session.execute(
            select(User).where(User.role == UserRole.SUPER_ADMIN)
        ).scalar_one_or_none()
        
        if existing_admin:
            print(f"✅ Super Admin already exists: {existing_admin.email}")
            print("Skipping seed...")
            return
        
        # Default credentials
        email = "admin@msuite.com"
        password = "Admin@123"
        full_name = "Super Admin"
        
        # Create Super Admin user
        admin_user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=UserRole.SUPER_ADMIN,
            is_active=True
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        print("\n" + "="*60)
        print("🎉 Database seeded successfully!")
        print("="*60)
        print(f"\n📧 Super Admin Created:")
        print(f"   Email:    {email}")
        print(f"   Password: {password}")
        print(f"   Name:     {full_name}")
        print(f"   Role:     {admin_user.role.value}")
        print(f"   ID:       {admin_user.id}")
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    print("\n🌱 Starting database seed...\n")
    seed_database()
