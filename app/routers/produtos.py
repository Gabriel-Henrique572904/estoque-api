from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ProdutoAtualizar,
    ProdutoCriar,
    ProdutoResposta,
)
from app.services import produtos as servico


router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
)

Banco = Annotated[Session, Depends(get_db)]
IdProduto = Annotated[int, Path(gt=0)]


@router.post(
    "",
    response_model=ProdutoResposta,
    status_code=201,
    summary="Cadastrar produto com estoque inicial zero",
    responses={
        404: {"description": "Categoria não encontrada."},
        409: {
            "description": "SKU duplicado ou categoria indisponível."
        },
    },
)
def criar_produto(dados: ProdutoCriar, db: Banco):
    return servico.criar_produto(db, dados)


@router.get(
    "",
    response_model=list[ProdutoResposta],
    summary="Listar produtos",
)
def listar_produtos(
    db: Banco,
    offset: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=100),
    categoria_id: int | None = Query(default=None, gt=0),
):
    return servico.listar_produtos(
        db,
        offset,
        limite,
        categoria_id,
    )


@router.get(
    "/{produto_id}",
    response_model=ProdutoResposta,
    summary="Consultar produto pelo ID",
    responses={
        404: {"description": "Produto não encontrado."},
    },
)
def buscar_produto(produto_id: IdProduto, db: Banco):
    return servico.buscar_produto(db, produto_id)


@router.put(
    "/{produto_id}",
    response_model=ProdutoResposta,
    summary="Atualizar cadastro do produto",
    description=(
        "Substitui os dados cadastrais do produto. "
        "O estoque é alterado somente por movimentações."
    ),
    responses={
        404: {"description": "Produto ou categoria não encontrados."},
        409: {
            "description": "SKU duplicado ou categoria indisponível."
        },
    },
)
def atualizar_produto(
    produto_id: IdProduto,
    dados: ProdutoAtualizar,
    db: Banco,
):
    return servico.atualizar_produto(db, produto_id, dados)


@router.delete(
    "/{produto_id}",
    status_code=204,
    response_class=Response,
    summary="Excluir produto sem movimentações",
    responses={
        404: {"description": "Produto não encontrado."},
        409: {"description": "O produto possui movimentações."},
    },
)
def excluir_produto(produto_id: IdProduto, db: Banco):
    servico.excluir_produto(db, produto_id)
    return Response(status_code=204)