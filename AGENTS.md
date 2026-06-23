# AGENTS.md — claude-status-bot

Telegram bot que monitora mudanças de status do Claude pelo RSS em https://status.claude.com/history.rss.

## Projeto

- Bot Python (Telegram) que periodicamente consulta o RSS de status do Claude e notifica via Telegram quando há mudanças.
- Ainda sem código — repo vazio. As decisões de framework e lib (python-telegram-bot / aiogram, httpx / aiohttp, feedparser, etc.) estão por definir.

## Convenções (herdadas do ~/.claude/CLAUDE.md)

- **Idioma:** português do Brasil sempre.
- **WSL:** caminhos `C:\...` devem ser convertidos para `/mnt/c/...`.
- **Cross-project:** nunca modificar arquivos de outro projeto. Se uma mudança exige alteração em repositório vizinho, gerar spec em markdown em `./docs/handoff/` e informar o caminho absoluto ao usuário.
- **Git:**
  - `git commit` como save point antes de mudanças grandes. `git push` apenas quando ordenado.
  - `super commit` = `git add` criterioso dos não-rastreados + commit + push.
- **Implementação de specs externos:** usar a skill `implement` quando receber um documento de handoff de outro projeto.

## Setup (a preencher quando definido)

- `pip install -r requirements.txt`
- Variáveis de ambiente necessárias (ex.: `TELEGRAM_BOT_TOKEN`).
- Comandos: lint, typecheck, teste.
