"""
tests/test_sistema.py
Testes automatizados do núcleo de regras de negócio (GerenciadorProducao).

Executar (a partir da raiz do projeto):
    python -m unittest discover -s tests -v
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sistema import (  # noqa: E402
    GerenciadorProducao,
    IdDuplicadoError,
    PecaNaoEncontradaError,
    RemocaoInvalidaError,
)


class TestGerenciadorProducao(unittest.TestCase):
    def setUp(self) -> None:
        self.arquivo = Path("dados_teste_temp.json")
        if self.arquivo.exists():
            self.arquivo.unlink()
        self.gerenciador = GerenciadorProducao(arquivo_dados=self.arquivo)

    def tearDown(self) -> None:
        if self.arquivo.exists():
            self.arquivo.unlink()

    # -- Regras de qualidade -------------------------------------------------
    def test_peca_aprovada_dentro_das_regras(self):
        peca = self.gerenciador.cadastrar_peca("A1", 100, "azul", 15)
        self.assertEqual(peca.status, "Aprovada")
        self.assertEqual(peca.numero_caixa, 1)

    def test_peca_reprovada_por_peso(self):
        peca = self.gerenciador.cadastrar_peca("A2", 50, "azul", 15)
        self.assertEqual(peca.status, "Reprovada")
        self.assertTrue(any("Peso" in m for m in peca.motivos_reprovacao))

    def test_peca_reprovada_por_cor(self):
        peca = self.gerenciador.cadastrar_peca("A3", 100, "amarelo", 15)
        self.assertEqual(peca.status, "Reprovada")
        self.assertTrue(any("Cor" in m for m in peca.motivos_reprovacao))

    def test_peca_reprovada_por_comprimento(self):
        peca = self.gerenciador.cadastrar_peca("A4", 100, "azul", 30)
        self.assertEqual(peca.status, "Reprovada")
        self.assertTrue(any("Comprimento" in m for m in peca.motivos_reprovacao))

    def test_peca_reprovada_por_multiplos_motivos(self):
        peca = self.gerenciador.cadastrar_peca("A5", 50, "amarelo", 30)
        self.assertEqual(len(peca.motivos_reprovacao), 3)

    def test_limites_inclusivos_sao_aprovados(self):
        # 95g, 105g, 10cm e 20cm são os limites — devem ser aprovados (inclusive).
        p1 = self.gerenciador.cadastrar_peca("LIM1", 95, "azul", 10)
        p2 = self.gerenciador.cadastrar_peca("LIM2", 105, "verde", 20)
        self.assertEqual(p1.status, "Aprovada")
        self.assertEqual(p2.status, "Aprovada")

    def test_cor_e_case_insensitive(self):
        peca = self.gerenciador.cadastrar_peca("A6", 100, "AZUL", 15)
        self.assertEqual(peca.status, "Aprovada")

    # -- Cadastro / duplicidade ----------------------------------------------
    def test_id_duplicado_gera_erro(self):
        self.gerenciador.cadastrar_peca("B1", 100, "azul", 15)
        with self.assertRaises(IdDuplicadoError):
            self.gerenciador.cadastrar_peca("B1", 100, "verde", 15)

    def test_id_vazio_gera_erro(self):
        with self.assertRaises(ValueError):
            self.gerenciador.cadastrar_peca("   ", 100, "azul", 15)

    # -- Caixas ----------------------------------------------------------------
    def test_caixa_fecha_ao_atingir_dez_pecas(self):
        for i in range(10):
            self.gerenciador.cadastrar_peca(f"C{i}", 100, "azul", 15)
        self.assertEqual(len(self.gerenciador.caixas_fechadas), 1)
        self.assertTrue(self.gerenciador.caixas_fechadas[0].fechada)
        self.assertEqual(len(self.gerenciador.caixas_fechadas[0].pecas), 10)

    def test_nova_caixa_apos_fechar_anterior(self):
        for i in range(11):
            self.gerenciador.cadastrar_peca(f"D{i}", 100, "azul", 15)
        self.assertEqual(len(self.gerenciador.caixas_fechadas), 1)
        self.assertEqual(len(self.gerenciador.caixa_atual.pecas), 1)

    def test_pecas_reprovadas_nao_ocupam_caixa(self):
        self.gerenciador.cadastrar_peca("D_REP", 50, "azul", 15)
        self.assertEqual(len(self.gerenciador.caixa_atual.pecas), 0)

    # -- Remoção ----------------------------------------------------------------
    def test_remover_peca_reprovada(self):
        self.gerenciador.cadastrar_peca("E1", 50, "azul", 15)
        self.gerenciador.remover_peca("E1")
        self.assertNotIn("E1", self.gerenciador.pecas)

    def test_remover_peca_em_caixa_aberta(self):
        self.gerenciador.cadastrar_peca("F1", 100, "azul", 15)
        self.gerenciador.remover_peca("F1")
        self.assertNotIn("F1", self.gerenciador.pecas)
        self.assertEqual(len(self.gerenciador.caixa_atual.pecas), 0)

    def test_remover_peca_em_caixa_fechada_falha(self):
        for i in range(10):
            self.gerenciador.cadastrar_peca(f"G{i}", 100, "azul", 15)
        with self.assertRaises(RemocaoInvalidaError):
            self.gerenciador.remover_peca("G0")

    def test_remover_peca_inexistente_falha(self):
        with self.assertRaises(PecaNaoEncontradaError):
            self.gerenciador.remover_peca("NAO_EXISTE")

    # -- Relatório ----------------------------------------------------------------
    def test_relatorio_contabiliza_corretamente(self):
        self.gerenciador.cadastrar_peca("H1", 100, "azul", 15)      # aprovada
        self.gerenciador.cadastrar_peca("H2", 50, "azul", 15)       # reprovada peso
        self.gerenciador.cadastrar_peca("H3", 100, "amarelo", 15)   # reprovada cor
        relatorio = self.gerenciador.gerar_relatorio()
        self.assertEqual(relatorio["total_aprovadas"], 1)
        self.assertEqual(relatorio["total_reprovadas"], 2)
        self.assertEqual(relatorio["total_pecas_cadastradas"], 3)

    def test_relatorio_conta_caixas_usadas(self):
        for i in range(12):  # 1 caixa fechada (10) + 2 na caixa atual
            self.gerenciador.cadastrar_peca(f"I{i}", 100, "azul", 15)
        relatorio = self.gerenciador.gerar_relatorio()
        self.assertEqual(relatorio["quantidade_caixas_usadas"], 2)

    # -- Persistência ----------------------------------------------------------------
    def test_persistencia_recarrega_estado(self):
        self.gerenciador.cadastrar_peca("J1", 100, "azul", 15)
        gerenciador2 = GerenciadorProducao(arquivo_dados=self.arquivo)
        self.assertIn("J1", gerenciador2.pecas)
        self.assertEqual(gerenciador2.pecas["J1"].status, "Aprovada")


if __name__ == "__main__":
    unittest.main()
