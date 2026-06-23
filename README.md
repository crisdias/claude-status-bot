# claude-status-bot

Telegram bot that monitors [Claude Status](https://status.claude.com) changes via RSS and sends notifications when incidents are created or updated.

**Vibe coded** with [OpenCode](https://opencode.ai) (model: `opencode/deepseek-v4-flash-free`).

## How it works

- Polls `https://status.claude.com/history.rss` every `POLL_INTERVAL_SECONDS` (default: 300)
- Tracks each incident by its `<guid>` and the number of `<p>` entries in `<description>`
- On the **first run**, it populates state silently (no notifications)
- On subsequent runs, it notifies:
  - **New incidents** (unseen `<guid>`)
  - **Updates** (existing incident with more `<p>` entries)
- Incident lifecycle: `Investigating` → `Identified` → `Update*` → `Monitoring` → `Resolved`
- State is persisted in `state.json` — delete it to reset (next run will be treated as first)

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# fill in TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
.venv/bin/python main.py
```

## Environment

| Variable | Required | Default |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | yes | — |
| `TELEGRAM_CHAT_ID` | yes | — |
| `POLL_INTERVAL_SECONDS` | no | `300` |
| `STATE_FILE` | no | `state.json` |
| `LLM_PROVIDER` | no (translation) | — (`openrouter` or `ollama`) |
| `TRANSLATE_TO` | no | — (e.g. `pt-br`) |
| `OPENROUTER_KEY` | if provider=openrouter | — |
| `OPENROUTER_MODEL` | no | `meta-llama/llama-3.1-8b-instruct` |
| `OLLAMA_ENDPOINT` | no | `http://localhost:11434` |
| `OLLAMA_MODEL` | no | `gemma3:4b` |

## Test

```bash
.venv/bin/python test_notify.py
```

## Project

| File | Role |
|---|---|
| `main.py` | Entry point — async polling loop |
| `rss_monitor.py` | RSS fetch + parse |
| `notifier.py` | Telegram message dispatch |
| `state.py` | JSON state persistence |
| `translator.py` | Optional LLM translation (OpenRouter / Ollama) |
| `test_notify.py` | Quick connectivity test |
