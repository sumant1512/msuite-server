"""
Product review service for business logic
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from typing import List, Optional, Dict
from uuid import UUID

from app.models.review import ProductReview
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewService:
    """Service for product review operations"""

    @staticmethod
    def create_review(
        db: Session,
        customer_id: UUID,
        review_data: ReviewCreate
    ) -> ProductReview:
        """Create a new product review"""
        # Check if order_id is provided to mark as verified purchase
        is_verified = review_data.order_id is not None
        
        review = ProductReview(
            customer_id=customer_id,
            is_verified_purchase=is_verified,
            **review_data.model_dump()
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def get_review_by_id(
        db: Session,
        review_id: UUID
    ) -> Optional[ProductReview]:
        """Get review by ID"""
        return db.query(ProductReview).filter(ProductReview.id == review_id).first()

    @staticmethod
    def get_product_reviews(
        db: Session,
        product_id: UUID,
        skip: int = 0,
        limit: int = 100,
        approved_only: bool = True
    ) -> List[ProductReview]:
        """Get all reviews for a product"""
        query = db.query(ProductReview).filter(ProductReview.product_id == product_id)
        
        if approved_only:
            query = query.filter(ProductReview.is_approved == True)
        
        return query.order_by(ProductReview.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_customer_reviews(
        db: Session,
        customer_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProductReview]:
        """Get all reviews by a customer"""
        return db.query(ProductReview).filter(
            ProductReview.customer_id == customer_id
        ).order_by(ProductReview.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_review(
        db: Session,
        review: ProductReview,
        review_data: ReviewUpdate
    ) -> ProductReview:
        """Update a review"""
        update_data = review_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)
        
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def delete_review(
        db: Session,
        review: ProductReview
    ) -> None:
        """Delete a review"""
        db.delete(review)
        db.commit()

    @staticmethod
    def moderate_review(
        db: Session,
        review: ProductReview,
        is_approved: bool
    ) -> ProductReview:
        """Approve or reject a review"""
        review.is_approved = is_approved
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def increment_helpful_count(
        db: Session,
        review: ProductReview
    ) -> ProductReview:
        """Increment helpful count for a review"""
        review.helpful_count += 1
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def get_product_review_stats(
        db: Session,
        product_id: UUID
    ) -> Dict:
        """Get review statistics for a product"""
        # Get all approved reviews
        reviews = db.query(ProductReview).filter(
            and_(
                ProductReview.product_id == product_id,
                ProductReview.is_approved == True
            )
        ).all()
        
        if not reviews:
            return {
                "average_rating": 0.0,
                "total_reviews": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "verified_purchase_count": 0
            }
        
        # Calculate statistics
        total_reviews = len(reviews)
        total_rating = sum(r.rating for r in reviews)
        average_rating = round(total_rating / total_reviews, 2)
        
        # Rating distribution
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1
        
        # Verified purchases
        verified_count = sum(1 for r in reviews if r.is_verified_purchase)
        
        return {
            "average_rating": average_rating,
            "total_reviews": total_reviews,
            "rating_distribution": rating_distribution,
            "verified_purchase_count": verified_count
        }

    @staticmethod
    def check_customer_purchased_product(
        db: Session,
        customer_id: UUID,
        product_id: UUID
    ) -> bool:
        """Check if customer has purchased the product"""
        from app.models.order import Order, OrderItem
        
        result = db.query(Order).join(OrderItem).filter(
            and_(
                Order.customer_id == customer_id,
                OrderItem.product_id == product_id,
                Order.status.in_(["CONFIRMED", "SHIPPED", "DELIVERED"])
            )
        ).first()
        return result is not None
