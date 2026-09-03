from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Movimentacao, Produto
from app.schemas import MovimentacaoCriar


def buscar_movimentacao(db: Session, movimentacao_id: int):
    movimentacao = db.get(Movimentacao, movimentacao_id)

    if movimentacao is None:
        raise HTTPException(
            status_code=404,
            detail="Movimentação não encontrada.",
        )

    return movimentacao


def listar_movimentacoes(
    db: Session,
    offset: int,
    limite: int,
    produto_id: int | None = None,
):
    consulta = select(Movimentacao)

    if produto_id is not None:
        consulta = consulta.where(
            Movimentacao.produto_id == produto_id
        )

    consulta = (
        consulta
        .order_by(Movimentacao.id.desc())
        .offset(offset)
        .limit(limite)
    )

    return db.scalars(consulta).all()


def criar_movimentacao(db: Session, dados: MovimentacaoCriar):
    comando = update(Produto).where(
        Produto.id == dados.produto_id
    )

    if dados.tipo == "ENTRADA":
        comando = comando.values(
            estoque=Produto.estoque + dados.quantidade
        )
    else:
        comando = (
            comando
            .where(Produto.estoque >= dados.quantidade)
            .values(
                estoque=Produto.estoque - dados.quantidade
            )
        )

    try:
        resultado = db.execute(
            comando.execution_options(synchronize_session=False)
        )

        if resultado.rowcount == 0:
            produto = db.get(Produto, dados.produto_id)

            if produto is None:
                raise HTTPException(
                    status_code=404,
                    detail="Produto não encontrado.",
                )

            raise HTTPException(
                status_code=409,
                detail="Estoque insuficiente para realizar a saída.",
            )

        movimentacao = Movimentacao(**dados.model_dump())
        db.add(movimentacao)
        db.flush()
        db.refresh(movimentacao)
        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Conflito ao registrar a movimentação.",
        ) from erro

    except SQLAlchemyError as erro:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Não foi possível registrar a movimentação.",
        ) from erro

    return movimentacao