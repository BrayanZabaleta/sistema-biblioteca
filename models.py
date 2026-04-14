from sqlalchemy import Column, Integer, String, Date, ForeignKey
from database import Base

class Libro(Base):
    __tablename__ = "Libros"

    id_libro = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    autor = Column(String)
    categoria = Column(String)
    editorial = Column(String)
    fecha_publicacion = Column(Date)
    cantidad_disponible = Column(Integer)
    cantidad_total = Column(Integer)
    
class Prestamo(Base):
    __tablename__ = "Prestamos"

    id_prestamo = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"))
    id_libro = Column(Integer, ForeignKey("Libros.id_libro"))
    fecha_prestamo = Column(Date)
    fecha_devolucion_estimada = Column(Date)
    estado = Column(String)

class Devolucion(Base):
    __tablename__ = "Devoluciones"

    id_devoluciones = Column(Integer, primary_key=True, index=True)
    id_prestamo = Column(Integer, ForeignKey("Prestamos.id_prestamo"))
    fecha_devolucion_real = Column(Date)
    estado = Column(String)

class Multa(Base):
    __tablename__ = "Multas"

    id_multa = Column(Integer, primary_key=True, index=True)
    id_devolucion = Column(Integer, ForeignKey("Devoluciones.id_devoluciones"))
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"))
    dias_retraso = Column(Integer)
    monto = Column(Integer)
    estado = Column(String)

class Historial(Base):
    __tablename__ = "Historial"

    id_historial = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"))
    id_libro = Column(Integer, ForeignKey("Libros.id_libro"))
    fecha = Column(Date)
    accion = Column(String)

class Usuario(Base):
    __tablename__ = "Usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    rol = Column(String, default="usuario")