# AGENTS.md — claude-status-bot

Telegram bot que monitora mudanças de status do Claude pelo RSS em https://status.claude.com/history.rss.

## Estrutura

| Arquivo | Função |
|---|---|
| `main.py` | Entrypoint — loop assíncrono de polling |
| `rss_monitor.py` | Fetch + parse do RSS Statuspage |
| `notifier.py` | Envio de mensagens via Telegram |
| `state.py` | Persistência de estado em `state.json` (guids + contagem de updates vistos) |
| `requirements.txt` | Dependências (python-telegram-bot, httpx, feedparser, python-dotenv) |

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # preencher TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID
.venv/bin/python main.py
```

## Funcionamento

- A cada `POLL_INTERVAL_SECONDS` (default 300) consulta o RSS em `https://status.claude.com/history.rss`
- Cada incidente é identificado por `<guid>`; mudanças detectadas por aumento no número de `<p>` no `<description>`
- Na **primeira execução** apenas popula o estado sem notificar. A partir da segunda, notifica incidentes novos e atualizações
- Ciclo de vida de um incidente: `Investigating` → `Identified` → `Update*` → `Monitoring` → `Resolved`
- **Estado fica em `state.json`** — se deletado, a próxima execução conta como primeira e não notifica

## Variáveis de ambiente

| Variável | Obrigatória | Default |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | sim | — |
| `TELEGRAM_CHAT_ID` | sim | — |
| `POLL_INTERVAL_SECONDS` | não | `300` |
| `STATE_FILE` | não | `state.json` |

## Notas

- Apenas `main.py` é entrypoint. Rodar com `python main.py` dentro da venv.
- Não há lint/typecheck configurados (repo mínimo). Adicionar se crescer.
