"""
demo_dados.py
Popula o sistema com peças de exemplo, de forma NÃO interativa.

Serve para:
    - Gerar rapidamente dados de exemplo para o vídeo pitch.
    - Servir de referência de entradas/saídas para o README.

Uso:
    python demo_dados.py
"""
from pathlib import Path

from sistema import GerenciadorProducao

# (id, peso_g, cor, comprimento_cm) — inclui casos aprovados e reprovados
# de propósito, para demonstrar todas as regras de qualidade em ação.
EXEMPLOS = [
    ("P001", 98.0, "azul", 15.0),      # aprovada
    ("P002", 102.5, "verde", 12.0),    # aprovada
    ("P003", 90.0, "azul", 15.0),      # reprovada: peso
    ("P004", 100.0, "amarelo", 14.0),  # reprovada: cor
    ("P005", 99.0, "verde", 25.0),     # reprovada: comprimento
    ("P006", 96.0, "azul", 10.5),      # aprovada
    ("P007", 104.0, "verde", 19.5),    # aprovada
    ("P008", 95.0, "azul", 11.0),      # aprovada (limite inferior de peso)
    ("P009", 105.0, "verde", 20.0),    # aprovada (limite superior de peso/comprimento)
    ("P010", 100.0, "azul", 15.0),     # aprovada
    ("P011", 101.0, "verde", 16.0),    # aprovada
    ("P012", 89.5, "verde", 30.0),     # reprovada: peso e comprimento
]


def main() -> None:
    gerenciador = GerenciadorProducao(arquivo_dados=Path("dados_producao.json"))
    for id_peca, peso, cor, comprimento in EXEMPLOS:
        try:
            peca = gerenciador.cadastrar_peca(id_peca, peso, cor, comprimento)
            extra = f"(caixa #{peca.numero_caixa})" if peca.numero_caixa else ""
            print(f"{id_peca}: {peca.status} {extra}")
        except Exception as e:  # pragma: no cover - script de demonstração
            print(f"{id_peca}: erro ao cadastrar ({e})")

    relatorio = gerenciador.gerar_relatorio()
    gerenciador.salvar_relatorio_em_arquivo(relatorio)
    print("\nDados de exemplo cadastrados e relatório gerado "
          "('relatorio_final.txt' / 'relatorio_final.json').")


if __name__ == "__main__":
    main()
