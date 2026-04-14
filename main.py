from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, joinedload
import models, crud, schemas
from database import SessionLocal, engine
from auth import get_current_user, solo_admin
from fastapi.security import OAuth2PasswordRequestForm

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# conexión a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# endpoint
@app.get("/libros")
def listar_libros(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    return crud.get_libros(db)       
    """
    Permite listar todos los libros disponibles en la biblioteca.
    - Requiere autenticación
    - Retorna lista de libros con detalles
    """

@app.get("/prestamos")
def listar_prestamos(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.get_prestamos(db, user)
    """
    Permite listar todos los préstamos registrados en el sistema.
    - Requiere autenticación
    - Retorna lista de préstamos con detalles
    """

@app.get("/devoluciones")
def listar_devoluciones(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.get_devoluciones(db, user)
    """
    Permite listar todas las devoluciones registradas en el sistema.
    - Requiere autenticación
    - Retorna lista de devoluciones con detalles
    """

@app.get("/multas")
def listar_multas(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.get_mis_multas(db, user)
    """
    Permite listar todas las multas registradas en el sistema.
    - Requiere autenticación
    - Retorna lista de multas con detalles
    """

@app.get("/historial")
def ver_historial(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.get_mi_historial(db, user)
    """
    Permite ver el historial de actividades del usuario.
    - Requiere autenticación
    - Retorna lista de acciones realizadas por el usuario
    """

@app.post("/libros")
def crear_libro(
    libro: schemas.LibroBase, 
    db: Session = Depends(get_db), 
    user= Depends(get_current_user)):
    solo_admin(user)
    return crud.create_libro(db, libro)
    """
    Permite crear un nuevo libro en el sistema.
    - Valida datos de entrada
    - Registra en historial
    """

@app.post("/prestamos", summary="Registrar préstamo")
def crear_prestamo(
    prestamo: schemas.PrestamoBase, 
    db: Session = Depends(get_db), 
    user: dict = Depends(get_current_user)
    ):
    return crud.create_prestamo(db, prestamo, user)
    """
    Permite registrar un préstamo de libro.
    - Valida disponibilidad
    - Actualiza stock
    - Registra en historial
    """

@app.post("/devoluciones", summary="Registrar devolución")
def crear_devolucion(devolucion: schemas.DevolucionBase, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return crud.create_devolucion(db, devolucion, user)
    """
    Permite registrar una devolución de libro.
    - Actualiza estado del préstamo
    - Calcula multa si hay retraso
    - Actualiza historial
    """

@app.post("/registro")
def registro(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud.register_user(db, user)
    """
    Permite registrar un nuevo usuario.
    """

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return crud.login_user(
        db,
        schemas.UsuarioLogin(
            username=form_data.username,
            password=form_data.password
        )
    )
    """
    Permite a un usuario iniciar sesión y obtener un token JWT. 
    - Valida credenciales
    - Retorna token de acceso
    """
@app.get("/admin/usuarios")
def ver_usuarios(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    solo_admin(user)
    return db.query(models.Usuario).all()

@app.get("/admin/prestamos-detalle")
def ver_prestamos_detalle(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    solo_admin(user)

    return db.query(models.Prestamo).options(
        joinedload(models.Prestamo.libro),
        joinedload(models.Prestamo.usuario)
    ).all()
