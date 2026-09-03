from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Categoria
from app.schemas import CategoriaAtualizar, CategoriaCriar


def buscar_categoria(db: Session, categoria_id: int):
    categoria = db.get(Categoria, categoria_id)

    if categoria is None:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada.",
        )

    return categoria


def listar_categorias(db: Session, offset: int, limite: int):
    consulta = (
        select(Categoria)
        .order_by(Categoria.id)
        .offset(offset)
        .limit(limite)
    )

    return db.scalars(consulta).all()


def salvar_categoria(db: Session, categoria: Categoria):
    db.add(categoria)

    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Já existe uma categoria com esse nome.",
        ) from erro

    db.refresh(categoria)
    return categoria


def criar_categoria(db: Session, dados: CategoriaCriar):
    categoria = Categoria(nome=dados.nome)
    return salvar_categoria(db, categoria)


def atualizar_categoria(
    db: Session,
    categoria_id: int,
    dados: CategoriaAtualizar,
):
    categoria = buscar_categoria(db, categoria_id)
    categoria.nome = dados.nome

    return salvar_categoria(db, categoria)


def excluir_categoria(db: Session, categoria_id: int):
    categoria = buscar_categoria(db, categoria_id)
    db.delete(categoria)

    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não é possível excluir uma categoria que possui produtos.",
        ) from erro