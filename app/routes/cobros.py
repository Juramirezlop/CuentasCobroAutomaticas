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

@router.post("/cuentas-cobro/")
def crear_cuenta(cuenta: schemas.CuentaCobroCreate, db: Session = Depends(get_db)):
    persona = db.query(models.Persona).filter(models.Persona.id == cuenta.persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    nueva_cuenta = models.CuentaCobro(**cuenta.dict())
    db.add(nueva_cuenta)
    db.commit()
    db.refresh(nueva_cuenta)
    return {"msg": "Cuenta de cobro registrada", "id": nueva_cuenta.id}
