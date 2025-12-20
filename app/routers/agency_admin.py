"""
Agency Admin routes for e-commerce tenant management
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Annotated, List
import uuid

from app.core.dependencies import (
    get_db,
    require_agency_admin,
    require_agency_context
)
from app.models.user import User
from app.schemas.ecommerce import EcommerceCreate, EcommerceUpdate, EcommerceResponse, EcommerceStats
from app.services.ecommerce_service import EcommerceService


router = APIRouter(prefix="/agencies", tags=["Agency Admin"])


@router.post("/ecommerce", response_model=EcommerceResponse, status_code=status.HTTP_201_CREATED)
async def create_ecommerce(
    ecommerce_data: EcommerceCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)]
):
    """
    Create a new e-commerce tenant (Agency Admin only)
    
    Creates both the e-commerce tenant and an admin user account
    """
    ecommerce = EcommerceService.create_ecommerce(db, agency_id, ecommerce_data)
    return EcommerceResponse.model_validate(ecommerce)


@router.get("/ecommerce", response_model=List[EcommerceResponse])
async def list_ecommerce(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List all e-commerce tenants for the agency"""
    ecommerce_list = EcommerceService.list_ecommerce(db, agency_id, skip, limit)
    return [EcommerceResponse.model_validate(e) for e in ecommerce_list]


@router.get("/ecommerce/{ecommerce_id}", response_model=EcommerceResponse)
async def get_ecommerce(
    ecommerce_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)]
):
    """Get e-commerce tenant details"""
    ecommerce = EcommerceService.get_ecommerce(db, ecommerce_id)
    
    # Verify belongs to agency
    if ecommerce.agency_id != agency_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    return EcommerceResponse.model_validate(ecommerce)


@router.put("/ecommerce/{ecommerce_id}", response_model=EcommerceResponse)
async def update_ecommerce(
    ecommerce_id: uuid.UUID,
    ecommerce_data: EcommerceUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)]
):
    """Update e-commerce tenant"""
    ecommerce = EcommerceService.get_ecommerce(db, ecommerce_id)
    
    # Verify belongs to agency
    if ecommerce.agency_id != agency_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    ecommerce = EcommerceService.update_ecommerce(db, ecommerce_id, ecommerce_data)
    return EcommerceResponse.model_validate(ecommerce)


@router.delete("/ecommerce/{ecommerce_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ecommerce(
    ecommerce_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)]
):
    """Delete (deactivate) e-commerce tenant"""
    ecommerce = EcommerceService.get_ecommerce(db, ecommerce_id)
    
    # Verify belongs to agency
    if ecommerce.agency_id != agency_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    EcommerceService.delete_ecommerce(db, ecommerce_id)


@router.get("/ecommerce/{ecommerce_id}/stats", response_model=EcommerceStats)
async def get_ecommerce_stats(
    ecommerce_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)]
):
    """Get e-commerce statistics"""
    ecommerce = EcommerceService.get_ecommerce(db, ecommerce_id)
    
    # Verify belongs to agency
    if ecommerce.agency_id != agency_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    return EcommerceService.get_stats(db, ecommerce_id)


@router.post("/ecommerce/{ecommerce_id}/regenerate-api-key", status_code=status.HTTP_200_OK)
async def regenerate_api_key(
    ecommerce_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)]
):
    """
    Regenerate API key for an e-commerce tenant
    
    This endpoint allows agency admins to rotate API keys for security purposes.
    The old API key will be immediately invalidated.
    """
    ecommerce = EcommerceService.get_ecommerce(db, ecommerce_id)
    
    # Verify belongs to agency
    if ecommerce.agency_id != agency_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    new_api_key = EcommerceService.regenerate_api_key(db, ecommerce_id)
    
    return {
        "message": "API key regenerated successfully",
        "api_key": new_api_key,
        "ecommerce_id": str(ecommerce_id),
        "warning": "Save this key securely. It will not be shown again."
    }

