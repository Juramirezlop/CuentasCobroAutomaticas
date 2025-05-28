from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    personas = relationship("Persona", back_populates="owner")


class Persona(Base):
    __tablename__ = "personas"
    id = Column(Integer, primary_key=True, index=True)
    nombre_mio = Column(String)
    cedula = Column(String)
    lugar_cedula = Column(String)
    numero_cuenta = Column(String)
    nombre_persona = Column(String)
    nombre_cuenta = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="personas")

    cuentas = relationship("CuentaCobro", back_populates="persona")


class CuentaCobro(Base):
    __tablename__ = "cuentas_cobro"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date)
    periodo = Column(String)
    valor_numerico = Column(String)
    valor_texto = Column(String)
    numero_cuenta = Column(String)

    persona_id = Column(Integer, ForeignKey("personas.id"))
    persona = relationship("Persona", back_populates="cuentas")
