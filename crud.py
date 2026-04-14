from auth import hash_password, verify_password, create_token
from sqlalchemy.orm import Session
from datetime import date
from fastapi import HTTPException
import models, schemas



def get_libros(db: Session):
    return db.query(models.Libro).all()

def create_libro(db: Session, libro: schemas.LibroBase):
    if libro.cantidad_disponible < 0 or libro.cantidad_total < 0:
        raise HTTPException(status_code=400, detail="Cantidades no pueden ser negativas")
    if libro.cantidad_disponible > libro.cantidad_total:
        raise HTTPException(status_code=400, detail="Disponible no puede ser mayor que total")
    nuevo_libro = models.Libro(**libro.dict())
    existe = db.query(models.Libro).filter(models.Libro.titulo == libro.titulo).first()
    if existe:
        raise HTTPException(status_code=400, detail="El libro ya existe")
    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)
    return nuevo_libro

def create_prestamo(db: Session, prestamo: schemas.PrestamoBase):

    # buscar libro
    libro = db.query(models.Libro).filter(models.Libro.id_libro == prestamo.id_libro).first()

    if not libro:
        raise HTTPException(status_code=404, detail="Libro no existe")

    if libro.cantidad_disponible <= 0:
        raise HTTPException(status_code=400, detail="No hay stock disponible")
    
    if prestamo.fecha_devolucion_estimada < prestamo.fecha_prestamo:
        raise HTTPException(status_code=400, detail="Fecha inválida")

    # crear préstamo
    nuevo = models.Prestamo(**prestamo.dict())
    db.add(nuevo)

    # actualizar stock
    libro.cantidad_disponible -= 1

    # después de crear préstamo
    historial = models.Historial(
        id_libro=prestamo.id_libro,
        fecha=date.today(),
        accion="prestamo"
    )
    db.add(historial)

    db.commit()
    db.refresh(nuevo)

    return nuevo

def create_devolucion(db: Session, devolucion: schemas.DevolucionBase):

    prestamo = db.query(models.Prestamo).filter(
        models.Prestamo.id_prestamo == devolucion.id_prestamo
    ).first()

    if not prestamo:
        raise HTTPException(status_code=404, detail="Prestamo no existe")
    if prestamo.estado == "devuelto":
        raise HTTPException(status_code=400, detail="Este préstamo ya fue devuelto")

    libro = db.query(models.Libro).filter(
        models.Libro.id_libro == prestamo.id_libro
    ).first()

    nueva = models.Devolucion(**devolucion.dict())
    db.add(nueva)

    # actualizar préstamo
    prestamo.estado = "devuelto"

    # devolver stock
    libro.cantidad_disponible += 1

    # historial devolución
    historial_dev = models.Historial(
        id_libro=prestamo.id_libro,
        fecha=date.today(),
        accion="devolucion"
    )
    db.add(historial_dev)

    db.commit()  # commit para generar ID de devolución antes de calcular multa
    db.refresh(nueva)

    # calcular multa
    dias_retraso = (devolucion.fecha_devolucion_real - prestamo.fecha_devolucion_estimada).days

    if dias_retraso > 0:
        multa = models.Multa(
            id_devolucion=nueva.id_devoluciones,
            monto=dias_retraso * 1000,
            dias_retraso=dias_retraso,
            estado="pendiente"
        )
        db.add(multa)
    
        # historial multa
        historial_multa = models.Historial(
            id_libro=prestamo.id_libro,
            fecha=date.today(),
            accion="multa"
        )
        db.add(historial_multa)

    # 🔥 UN SOLO COMMIT
    db.commit()
    db.refresh(nueva)

    return nueva


def register_user(db: Session, user: schemas.UsuarioCreate):

    existe = db.query(models.Usuario).filter(
        models.Usuario.username == user.username
    ).first()

    if existe:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    nuevo = models.Usuario(
        username=user.username,
        password=hash_password(user.password)
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {"mensaje": "Usuario creado"}

def login_user(db: Session, user: schemas.UsuarioLogin):

    db_user = db.query(models.Usuario).filter(
        models.Usuario.username == user.username
    ).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_token({"sub": db_user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

