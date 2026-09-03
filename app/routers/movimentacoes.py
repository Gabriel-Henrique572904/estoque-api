from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MovimentacaoCriar, MovimentacaoResposta
from app.services import movimentacoes as servico


router = APIRouter(
    prefix="/movimentacoes",
    tags=["Movimentações"],
)

Banco = Annotated[Session, Depends(get_db)]
IdMovimentacao = Annotated[int, Path(gt=0)]


@router.post(
    "",
    response_model=MovimentacaoResposta,
    status_code=201,
    summary="Registrar entrada ou saída de estoque",
    description=(
        "Registra a movimentação e atualiza o saldo do produto "
        "na mesma transação. Saídas exigem estoque suficiente."
    ),
    responses={
        404: {"description": "Produto não encontrado."},
        409: {
            "description": "Estoque insuficiente ou conflito no registro."
        },
        500: {
            "description": "Falha ao registrar a movimentação."
        },
    },
)
def criar_movimentacao(dados: MovimentacaoCriar, db: Banco):
    return servico.criar_movimentacao(db, dados)


@router.get(
    "",
    response_model=list[MovimentacaoResposta],
    summary="Listar histórico de movimentações",
)
def listar_movimentacoes(
    db: Banco,
    offset: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=100),
    produto_id: int | None = Query(default=None, gt=0),
):
    return servico.listar_movimentacoes(
        db,
        offset,
        limite,
        produto_id,
    )


@router.get(
    "/{movimentacao_id}",
    response_model=MovimentacaoResposta,
    summary="Consultar movimentação pelo ID",
    responses={
        404: {"description": "Movimentação não encontrada."},
    },
)
def buscar_movimentacao(
    movimentacao_id: IdMovimentacao,
    db: Banco,
):
    return servico.buscar_movimentacao(db, movimentacao_id)