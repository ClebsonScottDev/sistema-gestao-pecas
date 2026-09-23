# Desafio de Automação Digital: Gestão de Peças, Qualidade e Armazenamento

**Disciplina:** Algoritmos e Lógica de Programação  
**Instituição:** UniFECAF

---

## 1. Contextualização do desafio

Em uma linha de montagem industrial, a inspeção de qualidade decide o
destino de cada peça produzida: ela segue para o estoque/expedição ou é
descartada/retrabalhada. Quando essa inspeção é feita manualmente, três
problemas se acumulam com o volume de produção:

1. **Atraso operacional** — um inspetor humano tem um limite físico de
   quantas peças consegue medir e classificar por hora, criando um gargalo
   antes mesmo de a peça chegar à embalagem.
2. **Falhas de conferência** — critérios aplicados "de olho" (peso
   aproximado, cor a distância, comprimento estimado) variam de inspetor
   para inspetor e de turno para turno, gerando inconsistência na
   qualidade que chega ao cliente final.
3. **Custo de operação** — cada peça reprovada tarde demais no processo
   (por exemplo, já embalada) custa mais para corrigir do que uma peça
   identificada e desviada no momento da produção.

A automação digital do controle de qualidade resolve os três problemas ao
mesmo tempo: ela aplica os critérios de forma **determinística** (a mesma
peça sempre recebe o mesmo veredito, em qualquer turno), **instantânea**
(a decisão acontece no momento do cadastro, sem fila de inspeção) e
**rastreável** (cada reprovação fica registrada com o motivo exato,
permitindo à fábrica identificar padrões — por exemplo, se um fornecedor de
matéria-prima está entregando peças fora do peso combinado).

Este projeto prototipa, em Python, o "cérebro de decisão" desse sistema:
um programa que recebe os dados de cada peça, aplica as regras de
qualidade da empresa, organiza automaticamente as peças aprovadas em
caixas de expedição e produz relatórios gerenciais consolidados.

## 2. Estruturação do raciocínio lógico

O problema foi decomposto em quatro sub-problemas menores, cada um
resolvido com uma estrutura de programação específica:

### 2.1. Decisão: a peça é aprovada ou reprovada?

Cada peça precisa ser avaliada contra três critérios **independentes**:
peso (95g–105g), cor (azul ou verde) e comprimento (10cm–20cm). A decisão
de projeto aqui foi não usar uma cadeia de `if/elif/else` (que para no
primeiro critério que falhar), e sim três blocos `if` separados que
avaliam cada critério isoladamente e acumulam os motivos de falha em uma
lista. Essa escolha importa porque uma peça pode falhar em mais de um
critério ao mesmo tempo, e o relatório de qualidade precisa saber de
**todos** eles, não só do primeiro encontrado — é a diferença entre um
sistema que diz "essa peça está errada" e um que diz "essa peça está
errada porque o peso e o comprimento estão fora do padrão".

```python
if not (PESO_MIN_G <= self.peso <= PESO_MAX_G):
    motivos.append("Peso fora do padrão...")
if self.cor.strip().lower() not in CORES_VALIDAS:
    motivos.append("Cor não aceita...")
if not (COMPRIMENTO_MIN_CM <= self.comprimento <= COMPRIMENTO_MAX_CM):
    motivos.append("Comprimento fora do padrão...")

status = "Reprovada" if motivos else "Aprovada"
