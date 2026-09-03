from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models
from app.database import Base, engine
from app.routers import categorias, movimentacoes, produtos


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Estoque API",
    description="API para controle de produtos, categorias e movimentações de estoque.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(categorias.router)
app.include_router(produtos.router)
app.include_router(movimentacoes.router)


@app.get(
    "/",
    tags=["Status"],
    summary="Verificar funcionamento da API",
    response_model=dict[str, str],
)
def verificar_status():
    return {
        "status": "ok",
        "mensagem": "API de controle de estoque em funcionamento.",
    }