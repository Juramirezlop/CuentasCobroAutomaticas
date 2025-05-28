from pydantic import BaseModel
from datetime import date

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PersonaCreate(BaseModel):
    nombre_mio: str
    cedula: str
    lugar_cedula: str
    numero_cuenta: str
    nombre_persona: str
    nombre_cuenta: str

class CuentaCobroCreate(BaseModel):
    fecha: date
    periodo: str
    valor_numerico: str
    valor_texto: str
    numero_cuenta: str
    persona_id: int
