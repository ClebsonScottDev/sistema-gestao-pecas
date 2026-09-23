"""
sistema.py
Núcleo de regras de negócio do Sistema de Gestão de Peças, Qualidade e Armazenamento.

Responsável por:
    - Cadastrar peças e avaliá-las conforme as regras de qualidade.
    - Alocar peças aprovadas em caixas, respeitando a capacidade máxima (10 por caixa).
    - Remover peças cadastradas (enquanto não estiverem em uma caixa já fechada).
    - Gerar relatórios consolidados (total aprovadas, reprovadas + motivo, caixas usadas).
    - Persistir e recuperar o estado do sistema em disco (JSON), para que os dados
      não se percam entre uma execução e outra.

Trabalho de Algoritmos e Lógica de Programação - UniFECAF
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from models import CAPACIDADE_CAIXA, Caixa, Peca

ARQUIVO_DADOS_PADRAO = Path("dados_producao.json")
ARQUIVO_LOG = Path("producao.log")

logging.basicConfig(
    filename=str(ARQUIVO_LOG),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)


class IdDuplicadoError(Exception):
    """Levantado ao tentar cadastrar uma peça com um ID já existente."""


class PecaNaoEncontradaError(Exception):
    """Levantado ao tentar operar sobre uma peça inexistente."""


class RemocaoInvalidaError(Exception):
    """Levantado ao tentar remover uma peça que já está em uma caixa fechada."""


class GerenciadorProducao:
    """Orquestra o ciclo de vida das peças: cadastro, avaliação, armazenamento e relatórios."""

    def __init__(self, arquivo_dados: Path = ARQUIVO_DADOS_PADRAO) -> None:
        self.arquivo_dados = Path(arquivo_dados)
        self.pecas: Dict[str, Peca] = {}
        self.caixas_fechadas: List[Caixa] = []
        self._contador_caixas = 0
        self.caixa_atual: Caixa = self._nova_caixa()
        self.carregar_dados()

    # ------------------------------------------------------------------
    # Caixas
    # ------------------------------------------------------------------
    def _nova_caixa(self) -> Caixa:
        self._contador_caixas += 1
        return Caixa(numero=self._contador_caixas)

    def _alocar_em_caixa(self, peca: Peca) -> None:
        if self.caixa_atual.fechada:
            self.caixa_atual = self._nova_caixa()
        self.caixa_atual.adicionar(peca)
        if self.caixa_atual.fechada:
            logging.info("Caixa #%s fechada com %s peças.", self.caixa_atual.numero, CAPACIDADE_CAIXA)
            self.caixas_fechadas.append(self.caixa_atual)
            self.caixa_atual = self._nova_caixa()

    # ------------------------------------------------------------------
    # 1. Cadastrar nova peça
    # ------------------------------------------------------------------
    def cadastrar_peca(self, id: str, peso: float, cor: str, comprimento: float) -> Peca:
        id = str(id).strip()
        if not id:
            raise ValueError("O ID da peça não pode ser vazio.")
        if id in self.pecas:
            raise IdDuplicadoError(f"Já existe uma peça cadastrada com o ID '{id}'.")

        peca = Peca(id=id, peso=float(peso), cor=str(cor), comprimento=float(comprimento))
        peca.avaliar()
        self.pecas[id] = peca

        if peca.status == "Aprovada":
            self._alocar_em_caixa(peca)
            logging.info("Peça %s cadastrada e APROVADA (caixa #%s).", id, peca.numero_caixa)
        else:
            logging.info("Peça %s cadastrada e REPROVADA (%s).", id, "; ".join(peca.motivos_reprovacao))

        self.salvar_dados()
        return peca

    # ------------------------------------------------------------------
    # 2. Listar peças aprovadas/reprovadas
    # ------------------------------------------------------------------
    def listar_por_status(self, status: Optional[str] = None) -> List[Peca]:
        """status: 'Aprovada', 'Reprovada' ou None (retorna todas)."""
        pecas = list(self.pecas.values())
        if status:
            pecas = [p for p in pecas if p.status == status]
        return sorted(pecas, key=lambda p: p.id)

    # ------------------------------------------------------------------
    # 3. Remover peça cadastrada
    # ------------------------------------------------------------------
    def remover_peca(self, id: str) -> Peca:
        id = str(id).strip()
        peca = self.pecas.get(id)
        if peca is None:
            raise PecaNaoEncontradaError(f"Nenhuma peça encontrada com o ID '{id}'.")

        if peca.numero_caixa is not None:
            caixa_fechada = next(
                (c for c in self.caixas_fechadas if c.numero == peca.numero_caixa), None
            )
            if caixa_fechada is not None:
                raise RemocaoInvalidaError(
                    f"A peça '{id}' está na caixa #{peca.numero_caixa}, que já foi fechada. "
                    "Peças em caixas fechadas não podem ser removidas (garante rastreabilidade "
                    "do lote — decisão de design documentada no README)."
                )
            # está na caixa atual (ainda aberta) — remove dos dois lados
            self.caixa_atual.pecas = [p for p in self.caixa_atual.pecas if p.id != id]
            self.caixa_atual.fechada = False

        del self.pecas[id]
        logging.info("Peça %s removida do sistema.", id)
        self.salvar_dados()
        return peca

    # ------------------------------------------------------------------
    # 4. Listar caixas fechadas
    # ------------------------------------------------------------------
    def listar_caixas_fechadas(self) -> List[Caixa]:
        return list(self.caixas_fechadas)

    # ------------------------------------------------------------------
    # 5. Gerar relatório final
    # ------------------------------------------------------------------
    def gerar_relatorio(self) -> dict:
        aprovadas = self.listar_por_status("Aprovada")
        reprovadas = self.listar_por_status("Reprovada")

        motivos_contagem: Dict[str, int] = {}
        for p in reprovadas:
            for m in p.motivos_reprovacao:
                chave = m.split(" (")[0]  # agrupa por tipo de motivo (ex.: "Peso fora do padrão")
                motivos_contagem[chave] = motivos_contagem.get(chave, 0) + 1

        caixas_usadas = len(self.caixas_fechadas) + (1 if self.caixa_atual.pecas else 0)

        relatorio = {
            "gerado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_pecas_cadastradas": len(self.pecas),
            "total_aprovadas": len(aprovadas),
            "total_reprovadas": len(reprovadas),
            "motivos_reprovacao": motivos_contagem,
            "quantidade_caixas_usadas": caixas_usadas,
            "caixas_fechadas": len(self.caixas_fechadas),
            "caixa_atual_ocupacao": f"{len(self.caixa_atual.pecas)}/{CAPACIDADE_CAIXA}",
        }
        logging.info("Relatório final gerado: %s", relatorio)
        return relatorio

    def salvar_relatorio_em_arquivo(self, relatorio: dict, base_nome: str = "relatorio_final") -> None:
        Path(f"{base_nome}.json").write_text(
            json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        linhas = [
            "=" * 60,
            "RELATÓRIO FINAL - GESTÃO DE PEÇAS, QUALIDADE E ARMAZENAMENTO",
            "=" * 60,
            f"Gerado em: {relatorio['gerado_em']}",
            "-" * 60,
            f"Total de peças cadastradas : {relatorio['total_pecas_cadastradas']}",
            f"Total de peças aprovadas   : {relatorio['total_aprovadas']}",
            f"Total de peças reprovadas  : {relatorio['total_reprovadas']}",
            f"Quantidade de caixas usadas: {relatorio['quantidade_caixas_usadas']} "
            f"({relatorio['caixas_fechadas']} fechada(s) + caixa atual "
            f"{relatorio['caixa_atual_ocupacao']})",
            "-" * 60,
            "Motivos de reprovação:",
        ]
        if relatorio["motivos_reprovacao"]:
            for motivo, qtd in relatorio["motivos_reprovacao"].items():
                linhas.append(f"  - {motivo}: {qtd} ocorrência(s)")
        else:
            linhas.append("  (nenhuma reprovação registrada)")
        linhas.append("=" * 60)
        Path(f"{base_nome}.txt").write_text("\n".join(linhas), encoding="utf-8")

    # ------------------------------------------------------------------
    # Persistência (bônus: dados sobrevivem ao fechar o programa)
    # ------------------------------------------------------------------
    def salvar_dados(self) -> None:
        dados = {
            "contador_caixas": self._contador_caixas,
            "pecas": [p.to_dict() for p in self.pecas.values()],
            "caixas_fechadas": [c.to_dict() for c in self.caixas_fechadas],
            "caixa_atual": self.caixa_atual.to_dict(),
        }
        self.arquivo_dados.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")

    def carregar_dados(self) -> None:
        if not self.arquivo_dados.exists():
            return
        try:
            dados = json.loads(self.arquivo_dados.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logging.warning("Arquivo de dados corrompido ou ilegível - iniciando estado novo.")
            return

        self._contador_caixas = dados.get("contador_caixas", 0)
        for pd in dados.get("pecas", []):
            self.pecas[pd["id"]] = Peca.from_dict(pd)

        self.caixas_fechadas = []
        for cd in dados.get("caixas_fechadas", []):
            caixa = Caixa(numero=cd["numero"], fechada=cd["fechada"])
            caixa.pecas = [self.pecas[pid] for pid in cd["pecas"] if pid in self.pecas]
            self.caixas_fechadas.append(caixa)

        ca = dados.get("caixa_atual")
        if ca:
            self.caixa_atual = Caixa(numero=ca["numero"], fechada=ca["fechada"])
            self.caixa_atual.pecas = [self.pecas[pid] for pid in ca["pecas"] if pid in self.pecas]
        logging.info("Dados carregados de %s (%s peças).", self.arquivo_dados, len(self.pecas))
