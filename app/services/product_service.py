"""
Product service for managing e-commerce product catalog
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
import uuid

from app.models.product import Product
from app.models.inventory import Inventory
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """Product service class"""
    
    @staticmethod
    def create_product(
        db: Session,
        ecommerce_id: uuid.UUID,
        product_data: ProductCreate
    ) -> Product:
        """Create a new product with inventory"""
        # Check if SKU already exists for this e-commerce
        existing = db.query(Product).filter(
            Product.ecommerce_id == ecommerce_id,
            Product.sku == product_data.sku
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
        
        # Create product
        product_dict = product_data.model_dump(exclude={'initial_quantity', 'low_stock_threshold'})
        product = Product(
            id=uuid.uuid4(),
            ecommerce_id=ecommerce_id,
            **product_dict
        )
        
        db.add(product)
        db.flush()
        
        # Create inventory record
        inventory = Inventory(
            product_id=product.id,
            quantity=product_data.initial_quantity or 0,
            reserved=0,
            low_stock_threshold=product_data.low_stock_threshold or 10
        )
        
        db.add(inventory)
        db.commit()
        db.refresh(product)
        
        return product
    
    @staticmethod
    def get_product(db: Session, product_id: uuid.UUID) -> Product:
        """Get product by ID"""
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return product
    
    @staticmethod
    def list_products(
        db: Session,
        ecommerce_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        active_only: bool = False
    ) -> List[Product]:
        """List products for an e-commerce tenant"""
        query = db.query(Product).filter(Product.ecommerce_id == ecommerce_id)
        
        if category:
            query = query.filter(Product.category == category)
        
        if active_only:
            query = query.filter(Product.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_product(
        db: Session,
        product_id: uuid.UUID,
        product_data: ProductUpdate
    ) -> Product:
        """Update product"""
        product = ProductService.get_product(db, product_id)
        
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: uuid.UUID) -> None:
        """Delete (deactivate) product"""
        product = ProductService.get_product(db, product_id)
        product.is_active = False
        db.commit()
    
    @staticmethod
    def update_inventory(
        db: Session,
        product_id: uuid.UUID,
        quantity_change: int
    ) -> Inventory:
        """Update product inventory quantity"""
        inventory = db.query(Inventory).filter(
            Inventory.product_id == product_id
        ).first()
        
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory record not found"
            )
        
        new_quantity = inventory.quantity + quantity_change
        if new_quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient inventory"
            )
        
        inventory.quantity = new_quantity
        db.commit()
        db.refresh(inventory)
        
        return inventory
