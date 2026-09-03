from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)

    produtos: Mapped[list["Produto"]] = relationship(
        back_populates="categoria",
        passive_deletes="all",
    )


class Produto(Base):
    __tablename__ = "produtos"

    __table_args__ = (
        CheckConstraint("preco >= 0", name="ck_produto_preco"),
        CheckConstraint("estoque >= 0", name="ck_produto_estoque"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), unique=True)
    nome: Mapped[str] = mapped_column(String(120))
    descricao: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    estoque: Mapped[int] = mapped_column(Integer, default=0)

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"),
        index=True,
    )

    categoria: Mapped["Categoria"] = relationship(
        back_populates="produtos",
    )
    movimentacoes: Mapped[list["Movimentacao"]] = relationship(
        back_populates="produto",
        passive_deletes="all",
    )


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('ENTRADA', 'SAIDA')",
            name="ck_movimentacao_tipo",
        ),
        CheckConstraint(
            "quantidade > 0",
            name="ck_movimentacao_quantidade",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id", ondelete="RESTRICT"),
        index=True,
    )

    tipo: Mapped[str] = mapped_column(String(7))
    quantidade: Mapped[int] = mapped_column(Integer)

    observacao: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    data_hora: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
    )

    produto: Mapped["Produto"] = relationship(
        back_populates="movimentacoes",
    )