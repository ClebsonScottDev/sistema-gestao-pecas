"""
main.py
Ponto de entrada do Sistema de Gestão de Peças, Qualidade e Armazenamento.

Uso:
    python main.py

Consulte o README.md para instruções completas de instalação, uso e exemplos.
"""
from __future__ import annotations

import sys

from sistema import (
    GerenciadorProducao,
    IdDuplicadoError,
    PecaNaoEncontradaError,
    RemocaoInvalidaError,
)

# ---------------------------------------------------------------------------
# Cores ANSI para destacar aprovações/reprovações no terminal.
# Funciona em Linux, macOS e Windows 10+ sem depender de bibliotecas externas.
# ---------------------------------------------------------------------------
VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
CIANO = "\033[96m"
NEGRITO = "\033[1m"
RESET = "\033[0m"


def cor_status(status: str) -> str:
    return VERDE if status == "Aprovada" else VERMELHO


def ler_texto(mensagem: str) -> str:
    return input(mensagem).strip()


def ler_float(mensagem: str) -> float:
    while True:
        valor = input(mensagem).strip().replace(",", ".")
        try:
            return float(valor)
        except ValueError:
            print(f"{VERMELHO}Valor inválido. Digite um número (ex.: 98.5).{RESET}")


def exibir_cabecalho(titulo: str) -> None:
    print(f"\n{NEGRITO}{CIANO}{'=' * 62}{RESET}")
    print(f"{NEGRITO}{CIANO}{titulo.center(62)}{RESET}")
    print(f"{NEGRITO}{CIANO}{'=' * 62}{RESET}")


def menu_cadastrar(gerenciador: GerenciadorProducao) -> None:
    exibir_cabecalho("CADASTRAR NOVA PEÇA")
    id_peca = ler_texto("ID da peça: ")
    peso = ler_float("Peso (g): ")
    cor = ler_texto("Cor (azul/verde/outra): ")
    comprimento = ler_float("Comprimento (cm): ")

    try:
        peca = gerenciador.cadastrar_peca(id_peca, peso, cor, comprimento)
    except (IdDuplicadoError, ValueError) as e:
        print(f"{VERMELHO}Erro: {e}{RESET}")
        return

    cor_txt = cor_status(peca.status)
    print(f"\nResultado: {cor_txt}{NEGRITO}{peca.status.upper()}{RESET}")
    if peca.status == "Reprovada":
        for motivo in peca.motivos_reprovacao:
            print(f"  {VERMELHO}- {motivo}{RESET}")
    else:
        print(f"  Alocada na caixa #{peca.numero_caixa}")


def menu_listar(gerenciador: GerenciadorProducao) -> None:
    exibir_cabecalho("LISTAR PEÇAS APROVADAS / REPROVADAS")
    print("1. Todas")
    print("2. Somente aprovadas")
    print("3. Somente reprovadas")
    escolha = ler_texto("Escolha: ")
    status = {"2": "Aprovada", "3": "Reprovada"}.get(escolha)

    pecas = gerenciador.listar_por_status(status)
    if not pecas:
        print(f"{AMARELO}Nenhuma peça encontrada.{RESET}")
        return

    print(f"\n{'ID':<10}{'Peso(g)':<10}{'Cor':<10}{'Comp(cm)':<10}{'Status':<12}{'Caixa':<8}")
    print("-" * 62)
    for p in pecas:
        cor_txt = cor_status(p.status)
        caixa = p.numero_caixa if p.numero_caixa is not None else "-"
        print(
            f"{p.id:<10}{p.peso:<10.2f}{p.cor:<10}{p.comprimento:<10.2f}"
            f"{cor_txt}{p.status:<12}{RESET}{str(caixa):<8}"
        )
        if p.status == "Reprovada":
            for m in p.motivos_reprovacao:
                print(f"    {VERMELHO}\u21b3 {m}{RESET}")


def menu_remover(gerenciador: GerenciadorProducao) -> None:
    exibir_cabecalho("REMOVER PEÇA CADASTRADA")
    id_peca = ler_texto("ID da peça a remover: ")
    try:
        peca = gerenciador.remover_peca(id_peca)
        print(f"{VERDE}Peça '{peca.id}' removida com sucesso.{RESET}")
    except (PecaNaoEncontradaError, RemocaoInvalidaError) as e:
        print(f"{VERMELHO}Erro: {e}{RESET}")


def menu_caixas_fechadas(gerenciador: GerenciadorProducao) -> None:
    exibir_cabecalho("CAIXAS FECHADAS")
    caixas = gerenciador.listar_caixas_fechadas()
    if not caixas:
        print(f"{AMARELO}Nenhuma caixa fechada ainda.{RESET}")
    for c in caixas:
        ids = ", ".join(p.id for p in c.pecas)
        print(f"Caixa #{c.numero} - {len(c.pecas)} peças: {ids}")
    ocup = len(gerenciador.caixa_atual.pecas)
    if ocup:
        print(
            f"\n{AMARELO}Caixa atual (#{gerenciador.caixa_atual.numero}, ainda aberta): "
            f"{ocup}/10 peças{RESET}"
        )


def menu_relatorio(gerenciador: GerenciadorProducao) -> None:
    exibir_cabecalho("RELATÓRIO FINAL")
    relatorio = gerenciador.gerar_relatorio()
    print(f"Total de peças cadastradas : {relatorio['total_pecas_cadastradas']}")
    print(f"Total de peças aprovadas   : {VERDE}{relatorio['total_aprovadas']}{RESET}")
    print(f"Total de peças reprovadas  : {VERMELHO}{relatorio['total_reprovadas']}{RESET}")
    print(f"Quantidade de caixas usadas: {relatorio['quantidade_caixas_usadas']}")
    print("\nMotivos de reprovação:")
    if relatorio["motivos_reprovacao"]:
        for motivo, qtd in relatorio["motivos_reprovacao"].items():
            print(f"  - {motivo}: {qtd}")
    else:
        print("  (nenhuma)")

    gerenciador.salvar_relatorio_em_arquivo(relatorio)
    print(f"\n{CIANO}Relatório salvo em 'relatorio_final.txt' e 'relatorio_final.json'.{RESET}")


def exibir_menu_principal() -> None:
    exibir_cabecalho("SISTEMA DE GESTÃO DE PEÇAS - LINHA DE MONTAGEM")
    print("1. Cadastrar nova peça")
    print("2. Listar peças aprovadas/reprovadas")
    print("3. Remover peça cadastrada")
    print("4. Listar caixas fechadas")
    print("5. Gerar relatório final")
    print("0. Sair")


def main() -> None:
    gerenciador = GerenciadorProducao()
    acoes = {
        "1": menu_cadastrar,
        "2": menu_listar,
        "3": menu_remover,
        "4": menu_caixas_fechadas,
        "5": menu_relatorio,
    }

    while True:
        exibir_menu_principal()
        escolha = ler_texto("\nEscolha uma opção: ")
        if escolha == "0":
            print(f"\n{CIANO}Encerrando o sistema. Dados salvos em 'dados_producao.json'.{RESET}")
            sys.exit(0)
        acao = acoes.get(escolha)
        if acao is None:
            print(f"{VERMELHO}Opção inválida. Tente novamente.{RESET}")
            continue
        acao(gerenciador)


if __name__ == "__main__":
    main()
