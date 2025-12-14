from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import check_db_connection
from app.models.ecommerce import Ecommerce
from app.schemas.ecommerce import EcommerceCreate

router = APIRouter()

@router.post("/")
def create_ecommerce(data: EcommerceCreate, agency_id: int, db: Session = Depends(check_db_connection)):
    ecommerce = Ecommerce(name=data.name, agency_id=agency_id)
    db.add(ecommerce)
    db.commit()
    return ecommerce