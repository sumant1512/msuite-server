from fastapi import FastAPI
from app.database import check_db_connection

app = FastAPI()


@app.on_event("startup")
def startup_event():
    check_db_connection()  # 🚨 If this fails → server won't start


@app.get("/")
def root():
    return {"status": "Server is running"}
