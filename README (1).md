# ZEUS GUARD
### O guardião pré-transação que fica entre você e o dreno

**HackQuest — Arbitrum Open House Singapore 2026** | Trilhas: Overall + Promising Products
**Autor:** Clebson Campos de Araujo (candidato PCD — narração do vídeo por voz sintética autorizada, IA declarada)

---

## 🎬 Demo (1min59s, voz do autor)

**Vídeo:** https://x0.at/Ury4.mp4

O vídeo mostra o smoke test real on-chain: um drainer bloqueado (`TooRisky`), valor acima do teto diário bloqueado (`AboveDailyCap`), transação sem sessão rejeitada (`NoSession`) e uma transação normal liberada em ~1 ms.

## ❌ O problema

Traders iniciantes na Arbitrum perdem dinheiro todos os dias para drainers e approvals falsos — e a única defesa existente é *depois* do dano: revogar aprovação, correr atrás do prejuízo. Quem está começando não tem muralha nenhuma.

## ✅ A solução

**ZEUS GUARD é um muro que fica ANTES da transação.** Antes de qualquer transferência sair da carteira, o contrato mede o endereço de destino, calcula um score de risco em tempo real e decide: passa ou morre.

```
[ carteira ] ==> [ ZEUS GUARD: mede o destino ] ==> [ destino ]
                        risco >= 6000  →  ⛔ TooRisky (transação morre antes do dreno)
```

## ⚙️ Como funciona

- **Contrato nativo Stylus (Rust)** — o guardião roda *dentro* da chain, não é serviço externo
- **Motor de risco QCSN** (seleção dissipativa quântica): cada transação é tratada como função de onda; só a de menor energia passa. Benchmark offline: **40/40 casos de teste, 1,1 ms/tx**
- **Regras do cofre:** risco máximo por destino, teto diário de gasto, sessões explícitas — tudo configurável pelo dono da carteira
- **Cofre USDG (Paxos Global Dollar)** pronto para o fluxo de pagamentos agênticos

## 🔗 Contrato deployado (verificável agora)

| Item | Valor |
|---|---|
| Contrato (Arbitrum Sepolia) | `0x313e9994f1e77f579e797c19e29250a9a782e3a5` |
| Explorer | https://sepolia.arbiscan.io/address/0x313e9994f1e77f579e797c19e29250a9a782e3a5 |
| Deploy (initcode) | `0xc893dbc4c59a1fd11abf054f1c4c81a6054b4da187df700a3f41e6a41c1fcfcb` |
| Ativação Stylus | `0x1e3515c1d6d9565fc12e0f4c2ae311ee77868131b23666a06de7d9f01773fe59` |
| Carteira de deploy | `0xf92721394140c43C72FbfF2f0ebf90327fD2bF9D` (testnet-only) |

### Smoke test on-chain (executado na Sepolia)

| Teste | Resultado | Seletor |
|---|---|---|
| `checkTx` → drainer (risco 6000) | ⛔ `TooRisky` | `0xcc65e730` |
| `checkTx` → 0,6 ETH com teto 0,5 | ⛔ `AboveDailyCap` | `0x73fede4c` |
| `checkTx` → sem sessão | ⛔ `NoSession` | `0xaabbee68` |

## 💰 Custo total do pipeline: US$ 0,00

Faucet PoW honesto (Sepolia) → ponte oficial depositEth → `cargo stylus deploy`. Nenhum centavo gasto; sobrou ~0,06 SepETH para demos e cache. **Fundação sobre infraestrutura simples, como a banca pede.**

## 🔮 Diferenciais para o futuro

- **Consciência pós-quântica:** o roadmap inclui score de risco quântico por endereço (pubkey exposta/reutilizada = colheita futura para Shor). Enquanto o mundo discute *quando*, o ZEUS GUARD já cobra a passagem
- **Nativo para a Robinhood Chain:** o design visa o ingresso de milhões de traders leigos — o público que mais precisa de um guardião pré-transação
- **Motor QCSN determinístico e auditável** — IA declarada, sem caixa-preta

## 🧪 Testes

- Smoke test on-chain: 3 bloqueios + 1 liberação (hashes acima, reproduzíveis no explorer)
- Benchmark QCSN offline: 40/40 classificações corretas, 1,1 ms/tx
- Suíte de testes reproduzíveis no repositório

## 📌 Próximos passos declarados

1. Deploy na Robinhood Chain testnet (trilha reservada)
2. Integração USDG no cofre
3. App de onboarding para não-técnicos (ZeroDev)

---

*Construído por Clebson Campos de Araujo com assistência de IA declarada (agente Guardião/ÉTER). Transparência radical: todos os números, hashes e custos desta página são verificáveis nos links acima.*
