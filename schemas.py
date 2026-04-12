from pydantic import BaseModel, Field
from datetime import date

class LibroBase(BaseModel):
    titulo: str
    autor: str
    categoria: str
    editorial: str
    fecha_publicacion: date
    cantidad_disponible: int
    cantidad_total: int

class Libro(LibroBase):
    id_libro: int

    class Config:
        from_attributes = True

class PrestamoBase(BaseModel):
    id_libro: int
    fecha_prestamo: date
    fecha_devolucion_estimada: date
    estado: str

class DevolucionBase(BaseModel):
    id_prestamo: int
    fecha_devolucion_real: date
    estado: str

class MultaBase(BaseModel):
    id_devolucion: int
    monto: int
    dias_retraso: int
    estado: str

class HistorialBase(BaseModel):
    id_libro: int
    fecha: date
    accion: str

class UsuarioCreate(BaseModel):
    username: str
    password: str = Field(min_length=4, max_length=72)

class UsuarioLogin(BaseModel):
    username: str
    password: str