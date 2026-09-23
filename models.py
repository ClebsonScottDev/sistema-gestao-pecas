"""
models.py
Modelos de dados do Sistema de Gestão de Peças, Qualidade e Armazenamento.

Define as estruturas fundamentais do domínio:
    - Peca:  representa uma peça produzida na linha de montagem.
    - Caixa: representa uma caixa de armazenamento com capacidade limitada.

Trabalho de Algoritmos e Lógica de Programação - UniFECAF
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# ---------------------------------------------------------------------------
# Regras de qualidade e capacidade — única fonte de verdade do sistema.
# Alterar aqui é suficiente para ajustar todo o comportamento do programa,
# sem precisar caçar números soltos pelo código (boa prática de manutenção).
# ---------------------------------------------------------------------------
PESO_MIN_G: float = 95.0
PESO_MAX_G: float = 105.0
CORES_VALIDAS: frozenset = frozenset({"azul", "verde"})
COMPRIMENTO_MIN_CM: float = 10.0
COMPRIMENTO_MAX_CM: float = 20.0
CAPACIDADE_CAIXA: int = 10


@dataclass
class Peca:
    """Representa uma peça produzida na linha de montagem."""

    id: str
    peso: float
    cor: str
    comprimento: float
    status: str = "Pendente"
    motivos_reprovacao: List[str] = field(default_factory=list)
    numero_caixa: Optional[int] = None  # preenchido se a peça for aprovada e alocada

    def avaliar(self) -> None:
        """Aplica as regras de qualidade e define o status/motivos da peça."""
        motivos: List[str] = []

        if not (PESO_MIN_G <= self.peso <= PESO_MAX_G):
            motivos.append(
                f"Peso fora do padrão ({self.peso:.2f}g; aceito {PESO_MIN_G:.0f}g-{PESO_MAX_G:.0f}g)"
            )
        if self.cor.strip().lower() not in CORES_VALIDAS:
            motivos.append(f"Cor não aceita ('{self.cor}'; aceitas: azul ou verde)")
        if not (COMPRIMENTO_MIN_CM <= self.comprimento <= COMPRIMENTO_MAX_CM):
            motivos.append(
                f"Comprimento fora do padrão ({self.comprimento:.2f}cm; aceito "
                f"{COMPRIMENTO_MIN_CM:.0f}cm-{COMPRIMENTO_MAX_CM:.0f}cm)"
            )

        self.motivos_reprovacao = motivos
        self.status = "Reprovada" if motivos else "Aprovada"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "peso": self.peso,
            "cor": self.cor,
            "comprimento": self.comprimento,
            "status": self.status,
            "motivos_reprovacao": self.motivos_reprovacao,
            "numero_caixa": self.numero_caixa,
        }

    @staticmethod
    def from_dict(dados: dict) -> "Peca":
        return Peca(
            id=dados["id"],
            peso=dados["peso"],
            cor=dados["cor"],
            comprimento=dados["comprimento"],
            status=dados.get("status", "Pendente"),
            motivos_reprovacao=dados.get("motivos_reprovacao", []),
            numero_caixa=dados.get("numero_caixa"),
        )


@dataclass
class Caixa:
    """Representa uma caixa de armazenamento de peças aprovadas (capacidade limitada)."""

    numero: int
    pecas: List[Peca] = field(default_factory=list)
    fechada: bool = False

    def esta_cheia(self) -> bool:
        return len(self.pecas) >= CAPACIDADE_CAIXA

    def adicionar(self, peca: Peca) -> None:
        if self.fechada:
            raise ValueError(f"Caixa #{self.numero} já está fechada.")
        if self.esta_cheia():
            raise ValueError(f"Caixa #{self.numero} já atingiu a capacidade máxima.")
        peca.numero_caixa = self.numero
        self.pecas.append(peca)
        if self.esta_cheia():
            self.fechada = True

    def to_dict(self) -> dict:
        return {
            "numero": self.numero,
            "fechada": self.fechada,
            "pecas": [p.id for p in self.pecas],
        }
