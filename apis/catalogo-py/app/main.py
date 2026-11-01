from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import Base, engine, get_session
from app.models import ProductoDB
from app.schemas import Producto, ProductoIn


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # crea la tabla si no existe
    yield


app = FastAPI(title="catalogo", version="0.2.0", lifespan=lifespan)
SessionDep = Annotated[Session, Depends(get_session)]


def buscar(session: Session, producto_id: int) -> ProductoDB:
    producto = session.get(ProductoDB, producto_id)
    if producto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Producto no encontrado")
    return producto


def guardar(session: Session, producto: ProductoDB) -> ProductoDB:
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un producto con ese nombre")
    session.refresh(producto)
    return producto


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/productos")
def listar(session: SessionDep) -> list[Producto]:
    return session.scalars(select(ProductoDB).order_by(ProductoDB.id)).all()


@app.get("/productos/{producto_id}")
def obtener(producto_id: int, session: SessionDep) -> Producto:
    return buscar(session, producto_id)


@app.post("/productos", status_code=status.HTTP_201_CREATED)
def crear(datos: ProductoIn, session: SessionDep) -> Producto:
    producto = ProductoDB(**datos.model_dump())
    session.add(producto)
    return guardar(session, producto)


@app.put("/productos/{producto_id}")
def actualizar(producto_id: int, datos: ProductoIn, session: SessionDep) -> Producto:
    producto = buscar(session, producto_id)
    for campo, valor in datos.model_dump().items():
        setattr(producto, campo, valor)
    return guardar(session, producto)


@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(producto_id: int, session: SessionDep):
    producto = buscar(session, producto_id)
    session.delete(producto)
    session.commit()

@app.get("/healthz")
def healthz():
    """Liveness: el proceso está vivo. No revisa dependencias."""
    return {"status": "ok"}


@app.get("/readyz")
def readyz(session: SessionDep):
    """Readiness: puede atender tráfico porque la base responde."""
    try:
        session.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Base de datos no disponible")
    return {"status": "ready"}