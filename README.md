# Sistema de Gestão de Peças, Qualidade e Armazenamento

Trabalho da disciplina **Algoritmos e Lógica de Programação** — UniFECAF.

Protótipo em Python que automatiza a inspeção de qualidade de peças em uma
linha de montagem: recebe os dados de cada peça, aplica as regras de
aprovação/reprovação, organiza as peças aprovadas em caixas de capacidade
limitada e gera relatórios consolidados de produção.

## Sumário

- [Contexto do desafio](#contexto-do-desafio)
- [Arquitetura e raciocínio lógico](#arquitetura-e-raciocínio-lógico)
- [Regras de negócio](#regras-de-negócio)
- [Estrutura de arquivos](#estrutura-de-arquivos)
- [Como instalar e executar](#como-instalar-e-executar)
- [Exemplos de entrada e saída](#exemplos-de-entrada-e-saída)
- [Testes automatizados](#testes-automatizados)
- [Decisões de design e desafios enfrentados](#decisões-de-design-e-desafios-enfrentados)
- [Reflexão: expansão para um cenário real](#reflexão-expansão-para-um-cenário-real)

## Contexto do desafio

Uma empresa industrial inspeciona peças manualmente antes de embalá-las,
o que gera atrasos, falhas de conferência e custo extra de operação. Este
projeto prototipa a automação digital dessa etapa: cada peça cadastrada é
avaliada automaticamente contra critérios de qualidade fixos (peso, cor e
comprimento) e o resultado decide o destino da peça — aprovação e
armazenamento em caixa, ou reprovação com o motivo registrado.

## Arquitetura e raciocínio lógico

O código é dividido em três camadas, para separar claramente **dados**,
**regras de negócio** e **interface com o usuário** (boa prática de
engenharia de software, mesmo em um protótipo pequeno):

| Arquivo | Responsabilidade |
|---|---|
| `models.py` | As entidades do domínio: `Peca` (com o método `avaliar()`, que aplica as três condições de qualidade) e `Caixa` (com a lógica de capacidade/fechamento). |
| `sistema.py` | `GerenciadorProducao`: orquestra cadastro, alocação em caixas, remoção, relatórios e persistência em disco (JSON). Contém toda a lógica condicional e de repetição do sistema. |
| `main.py` | O menu interativo (laço de repetição `while True` + estrutura de decisão `if/dict` para rotear a opção escolhida) e a formatação de saída no terminal. |

**Estruturas de controle usadas, mapeadas para o pedido do desafio:**

- **Decisão (`if`/`elif`):** `Peca.avaliar()` testa peso, cor e comprimento
  de forma independente e acumula **todos** os motivos de reprovação (uma
  peça pode falhar por mais de um critério ao mesmo tempo).
- **Repetição (`for`/`while`):** o menu principal roda em loop até a opção
  `0`; a avaliação de cada peça, a montagem das caixas e a contagem dos
  motivos de reprovação no relatório usam laços `for`.
- **Funções:** cada regra de negócio é uma função/método isolado e testável
  (`cadastrar_peca`, `remover_peca`, `gerar_relatorio`, `_alocar_em_caixa`...),
  em vez de um único bloco de código monolítico.
- **Tratamento de exceções:** erros de negócio (ID duplicado, peça
  inexistente, remoção inválida) são exceções customizadas (`IdDuplicadoError`,
  `PecaNaoEncontradaError`, `RemocaoInvalidaError`), capturadas na camada de
  interface e traduzidas em mensagens claras — o programa nunca quebra com
  uma entrada inválida.

## Regras de negócio

| Critério | Faixa aceita |
|---|---|
| Peso | 95g a 105g (inclusive) |
| Cor | azul ou verde (não sensível a maiúsculas/minúsculas) |
| Comprimento | 10cm a 20cm (inclusive) |
| Capacidade da caixa | 10 peças aprovadas por caixa |

Uma peça só precisa falhar em **um** critério para ser reprovada, mas o
sistema registra **todos** os motivos aplicáveis — útil para o relatório de
causas de reprovação.

## Estrutura de arquivos

```
trabalho_algoritmos/
├── main.py                 # menu interativo (ponto de entrada)
├── sistema.py               # regras de negócio + persistência (GerenciadorProducao)
├── models.py                 # entidades Peca e Caixa
├── demo_dados.py            # popula dados de exemplo (não interativo, útil para o vídeo pitch)
├── tests/
│   └── test_sistema.py       # 19 testes automatizados (unittest)
├── docs/
│   ├── documento_teorico.md  # Parte 1 do entregável (análise e discussão)
│   └── roteiro_video_pitch.md
├── dados_producao.json      # gerado em tempo de execução (estado persistido)
├── relatorio_final.txt/.json # gerado ao usar a opção 5 do menu
├── producao.log              # log de operações do sistema
├── README.md
├── LICENSE
└── .gitignore
```

## Como instalar e executar

Requer apenas **Python 3.10 ou superior** (testado em 3.11) — nenhuma
dependência externa.

```bash
# 1. Clone o repositório
git clone <URL_DO_SEU_REPOSITORIO>
cd trabalho_algoritmos

# 2. Execute o sistema
python main.py
```

Para gerar rapidamente dados de exemplo (útil antes de gravar o vídeo ou
para testar sem digitar manualmente):

```bash
python demo_dados.py
python main.py   # os dados de exemplo já estarão carregados
```

Para rodar os testes automatizados:

```bash
python -m unittest discover -s tests -v
```

## Exemplos de entrada e saída

**Cadastro de uma peça aprovada:**

```
Escolha uma opção: 1
ID da peça: P001
Peso (g): 98
Cor (azul/verde/outra): azul
Comprimento (cm): 15

Resultado: APROVADA
  Alocada na caixa #1
```

**Cadastro de uma peça reprovada por múltiplos motivos:**

```
Escolha uma opção: 1
ID da peça: P012
Peso (g): 89.5
Cor (azul/verde/outra): verde
Comprimento (cm): 30

Resultado: REPROVADA
  - Peso fora do padrão (89.50g; aceito 95g-105g)
  - Comprimento fora do padrão (30.00cm; aceito 10cm-20cm)
```

**Relatório final (opção 5), com os 12 exemplos de `demo_dados.py`:**

```
============================================================
RELATÓRIO FINAL - GESTÃO DE PEÇAS, QUALIDADE E ARMAZENAMENTO
============================================================
Total de peças cadastradas : 12
Total de peças aprovadas   : 8
Total de peças reprovadas  : 4
Quantidade de caixas usadas: 1 (0 fechada(s) + caixa atual 8/10)
------------------------------------------------------------
Motivos de reprovação:
  - Peso fora do padrão: 2 ocorrência(s)
  - Cor não aceita: 1 ocorrência(s)
  - Comprimento fora do padrão: 2 ocorrência(s)
============================================================
```

## Testes automatizados

O projeto inclui **19 testes unitários** (`tests/test_sistema.py`) cobrindo:
aprovação/reprovação por cada critério isolado e combinado, limites
inclusivos (95g/105g/10cm/20cm), duplicidade de ID, fechamento de caixa ao
atingir 10 peças, abertura de nova caixa, remoção de peça (permitida e
bloqueada quando já em caixa fechada), cálculo do relatório e persistência
em disco entre execuções.

```bash
$ python -m unittest discover -s tests -v
...
Ran 19 tests in 0.03s
OK
```

## Decisões de design e desafios enfrentados

- **Por que bloquear a remoção de peças em caixas já fechadas?** Uma caixa
  fechada representa um lote que já foi "selado" para expedição — permitir
  remoção depois quebraria a rastreabilidade do lote. Peças reprovadas ou
  ainda na caixa aberta podem ser removidas livremente (ex.: correção de
  erro de digitação).
- **Por que persistir em JSON em vez de manter tudo só em memória?** Para
  que o sistema simule um caso de uso real: a produção não para quando o
  operador fecha o programa. O maior desafio aqui foi decidir *quando*
  salvar — a solução foi salvar a cada operação de escrita (cadastro/
  remoção), garantindo que uma queda de energia não perca dados.
- **Por que acumular todos os motivos de reprovação, e não parar no
  primeiro?** Um relatório de qualidade real precisa saber *todas* as
  causas de uma peça defeituosa, não só a primeira encontrada — isso muda
  a lógica de `if/elif` (que para no primeiro `True`) para três `if`
  independentes que se acumulam em uma lista.
- **Desafio de teste:** simular o fechamento de caixas e a criação de caixas
  novas exigiu isolar cada teste com um arquivo de dados temporário
  (`setUp`/`tearDown`), para que um teste nunca "veja" o estado deixado por
  outro.

## Reflexão: expansão para um cenário real

Este protótipo em Python resolve o problema no nível **lógico**, mas o
caminho até uma linha de produção real passaria por três camadas de
evolução:

1. **Sensores físicos:** hoje o peso/cor/comprimento são digitados; numa
   fábrica real viriam de uma balança digital, uma câmera com sensor de cor
   (ou um sensor RGB dedicado) e um sensor a laser de distância, todos
   conectados a um microcontrolador (ex.: Arduino/ESP32) que envia os dados
   ao sistema via serial ou MQTT.
2. **Inteligência artificial:** os critérios hoje são regras fixas
   (thresholds). Um classificador de visão computacional (ex.: uma rede
   neural convolucional treinada em fotos de peças aprovadas/reprovadas)
   poderia detectar defeitos visuais que não se reduzem a "peso, cor,
   comprimento" — rachaduras, rebarbas, deformações — e um modelo de
   manutenção preditiva poderia usar o histórico de reprovações para
   prever falhas na linha antes que aconteçam.
3. **Integração industrial:** em vez de um menu de terminal, o sistema se
   tornaria um serviço (API REST) integrado a um sistema MES (Manufacturing
   Execution System) ou ERP, permitindo rastreamento em tempo real, alertas
   automáticos e dashboards de produção para os gestores da fábrica.

O núcleo lógico construído aqui — avaliação por critérios, alocação em
lotes de tamanho fixo, relatórios consolidados — continuaria sendo o
"cérebro" de decisão em qualquer uma dessas evoluções; o que mudaria é
apenas a **origem dos dados de entrada** e o **destino dos relatórios**.

---

**Autor:** Trabalho acadêmico — Algoritmos e Lógica de Programação (UniFECAF)
**Licença:** MIT (ver `LICENSE`)
