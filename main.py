import os
from typing import Optional
import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, Depends, Body, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models
from database import engine, SessionLocal
from models import Song

models.Base.metadata.create_all(bind=engine)


security = HTTPBearer()
# bearer_scheme = HTTPBearer()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
assert BEARER_TOKEN is not None


def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme != "Bearer" or credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return credentials


app = FastAPI()
# app = FastAPI(dependencies=[Depends(validate_token)])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme != "Bearer":
        raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return credentials.credentials

@app.get("/protected-endpoint")
def read_protected_endpoint(token: str = Depends(authenticate_user)):
    return {"message": "Welcome to the protected endpoint!"}

@app.get('/')
def read_root():
    return {'name': 'fastapi-songs'}


@app.get('/songs/')
def read_songs(db: Session = Depends(get_db)):
    return db.query(Song).all()


def start():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    start()