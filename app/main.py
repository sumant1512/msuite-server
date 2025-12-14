from fastapi import FastAPI
from app.database import check_db_connection

app = FastAPI(title="MSuite API")

@app.on_event("startup")
def startup():
    check_db_connection()


@app.get("/")
def root():
    return {"status": "Server is running"}
