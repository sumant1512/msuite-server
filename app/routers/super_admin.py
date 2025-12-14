from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.agency import Agency
from app.enums.user_role import UserRole
from app.schemas.agency import AgencyCreate

router = APIRouter(prefix="/super/agencies", tags=["Super Admin"])

@router.post("/")
def create_agency(data: AgencyCreate, db: Session = Depends(get_db)):

    # 1. Create agency admin user
    admin_user = User(
        name=data.admin_name,
        email=data.admin_email,
        password_hash=get_password_hash(data.admin_password),
        role=UserRole.AGENCY_ADMIN
    )
    db.add(admin_user)
    db.flush()  # <-- IMPORTANT (gets admin_user.id)

    # 2. Create agency linked to user
    agency = Agency(
        agency_name=data.agency_name,
        agency_email=data.agency_email,
        user_id=admin_user.id
    )

    db.add(agency)
    db.commit()

    return {
        "agency_id": agency.id,
        "agency_name": agency.agency_name,
        "agency_admin_id": admin_user.id
    }
