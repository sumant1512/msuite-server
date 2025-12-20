"""
MSuite - Multi-Tenant E-Commerce Backend-as-a-Service
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import check_db_connection
from app.core.config import settings
from app.routers import (
    auth,
    super_admin,
    agency_admin,
    user,
    product,
    order,
    customer,
    cart,
    coupon,
    webhook,
    review,
    audit_log,
    refund
)


# Create FastAPI application with OpenAPI security scheme
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-tenant e-commerce backend-as-a-service platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    """Run startup tasks"""
    check_db_connection()
    print(f"🚀 {settings.PROJECT_NAME} started successfully")


@app.get("/", tags=["Health"])
def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "v1"
    }


# Include routers with API v1 prefix
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(super_admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(agency_admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(user.router, prefix=settings.API_V1_PREFIX)
app.include_router(product.router, prefix=settings.API_V1_PREFIX)
app.include_router(order.router, prefix=settings.API_V1_PREFIX)
app.include_router(customer.router, prefix=settings.API_V1_PREFIX)
app.include_router(cart.router, prefix=settings.API_V1_PREFIX)
app.include_router(coupon.router, prefix=settings.API_V1_PREFIX)
app.include_router(webhook.router, prefix=settings.API_V1_PREFIX)
app.include_router(review.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_log.router, prefix=settings.API_V1_PREFIX)
app.include_router(refund.router, prefix=settings.API_V1_PREFIX)


