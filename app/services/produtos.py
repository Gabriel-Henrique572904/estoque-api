from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Produto
from app.schemas import ProdutoAtualizar, ProdutoCriar
from app.services.categorias import buscar_categoria


def buscar_produto(db: Session, produto_id: int):
    produto = db.get(Produto, produto_id)

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado.",
        )

    return produto


def listar_produtos(
    db: Session,
    offset: int,
    limite: int,
    categoria_id: int | None = None,
):
    consulta = select(Produto)

    if categoria_id is not None:
        consulta = consulta.where(
            Produto.categoria_id == categoria_id
        )

    consulta = (
        consulta
        .order_by(Produto.id)
        .offset(offset)
        .limit(limite)
    )

    return db.scalars(consulta).all()


def salvar_produto(db: Session, produto: Produto):
    db.add(produto)

    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Não foi possível salvar: "
                "SKU duplicado ou categoria indisponível."
            ),
        ) from erro

    db.refresh(produto)
    return produto


def criar_produto(db: Session, dados: ProdutoCriar):
    buscar_categoria(db, dados.categoria_id)

    produto = Produto(
        **dados.model_dump(),
        estoque=0,
    )

    return salvar_produto(db, produto)


def atualizar_produto(
    db: Session,
    produto_id: int,
    dados: ProdutoAtualizar,
):
    produto = buscar_produto(db, produto_id)
    buscar_categoria(db, dados.categoria_id)

    for campo, valor in dados.model_dump().items():
        setattr(produto, campo, valor)

    return salvar_produto(db, produto)


def excluir_produto(db: Session, produto_id: int):
    produto = buscar_produto(db, produto_id)
    db.delete(produto)

    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Não é possível excluir um produto "
                "que possui movimentações."
            ),
        ) from erro