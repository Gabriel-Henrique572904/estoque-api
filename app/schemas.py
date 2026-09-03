from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EsquemaBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
    )


class CategoriaCriar(EsquemaBase):
    nome: str = Field(
        min_length=1,
        max_length=100,
        examples=["Informática"],
    )


class CategoriaAtualizar(CategoriaCriar):
    pass


class CategoriaResposta(CategoriaCriar):
    id: int


class ProdutoCriar(EsquemaBase):
    sku: str = Field(
        min_length=1,
        max_length=40,
        examples=["PROD-001"],
    )
    nome: str = Field(
        min_length=1,
        max_length=120,
        examples=["Mouse USB"],
    )
    descricao: str | None = Field(
        default=None,
        max_length=500,
    )
    preco: Decimal = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
        examples=["29.90"],
    )
    categoria_id: int = Field(
        gt=0,
        strict=True,
        examples=[1],
    )

    @field_validator("sku", mode="before")
    @classmethod
    def padronizar_sku(cls, valor):
        if isinstance(valor, str):
            return valor.strip().upper()
        return valor


class ProdutoAtualizar(ProdutoCriar):
    pass


class ProdutoResposta(ProdutoCriar):
    id: int
    estoque: int = Field(ge=0)


class MovimentacaoCriar(EsquemaBase):
    produto_id: int = Field(
        gt=0,
        strict=True,
        examples=[1],
    )
    tipo: Literal["ENTRADA", "SAIDA"]
    quantidade: int = Field(
        gt=0,
        strict=True,
        examples=[10],
    )
    observacao: str | None = Field(
        default=None,
        max_length=500,
        examples=["Compra de mercadorias"],
    )


class MovimentacaoResposta(MovimentacaoCriar):
    id: int
    data_hora: datetime = Field(
        description="Data e hora do registro em UTC.",
    )