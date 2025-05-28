# app/auth.py
from passlib.context import CryptContext
from fastapi import Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from app.database import SessionLocal
from app.models import User
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario inválido")

    return user
