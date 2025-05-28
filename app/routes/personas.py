from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/personas/")
def crear_persona(persona: schemas.PersonaCreate, db: Session = Depends(get_db)):
    usuario = db.query(models.User).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="No hay usuario disponible")

    nueva_persona = models.Persona(**persona.dict(), owner_id=usuario.id)
    db.add(nueva_persona)
    db.commit()
    db.refresh(nueva_persona)
    return {"msg": "Persona registrada", "id": nueva_persona.id}
