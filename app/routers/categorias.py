from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CategoriaAtualizar,
    CategoriaCriar,
    CategoriaResposta,
)
from app.services import categorias as servico


router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"],
)

Banco = Annotated[Session, Depends(get_db)]
IdCategoria = Annotated[int, Path(gt=0)]


@router.post(
    "",
    response_model=CategoriaResposta,
    status_code=201,
    summary="Cadastrar categoria",
    responses={
        409: {"description": "Nome de categoria já cadastrado."},
    },
)
def criar_categoria(dados: CategoriaCriar, db: Banco):
    return servico.criar_categoria(db, dados)


@router.get(
    "",
    response_model=list[CategoriaResposta],
    summary="Listar categorias",
)
def listar_categorias(
    db: Banco,
    offset: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=100),
):
    return servico.listar_categorias(db, offset, limite)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaResposta,
    summary="Consultar categoria pelo ID",
    responses={
        404: {"description": "Categoria não encontrada."},
    },
)
def buscar_categoria(categoria_id: IdCategoria, db: Banco):
    return servico.buscar_categoria(db, categoria_id)


@router.put(
    "/{categoria_id}",
    response_model=CategoriaResposta,
    summary="Atualizar categoria",
    responses={
        404: {"description": "Categoria não encontrada."},
        409: {"description": "Nome de categoria já cadastrado."},
    },
)
def atualizar_categoria(
    categoria_id: IdCategoria,
    dados: CategoriaAtualizar,
    db: Banco,
):
    return servico.atualizar_categoria(db, categoria_id, dados)


@router.delete(
    "/{categoria_id}",
    status_code=204,
    response_class=Response,
    summary="Excluir categoria sem produtos",
    responses={
        404: {"description": "Categoria não encontrada."},
        409: {"description": "A categoria possui produtos vinculados."},
    },
)
def excluir_categoria(categoria_id: IdCategoria, db: Banco):
    servico.excluir_categoria(db, categoria_id)
    return Response(status_code=204)