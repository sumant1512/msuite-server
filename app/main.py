from fastapi import FastAPI
from app.core.database import check_db_connection
# from app.routers import auth, super_admin, agency_admin, ecommerce, product

app = FastAPI(title="MSuite API")

@app.on_event("startup")
def startup():
    check_db_connection()


@app.get("/")
def root():
    return {"status": "Server is running"}

# app.include_router(auth.router, prefix="/auth")
# app.include_router(super_admin.router, prefix="/super-admin")
# app.include_router(agency_admin.router, prefix="/agency")
# app.include_router(ecommerce.router, prefix="/ecommerce")
# app.include_router(product.router, prefix="/products")

