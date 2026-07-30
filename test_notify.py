"""Envia uma mensagem de teste no Telegram para verificar a configuração.

Uso:
  .venv/bin/python test_notify.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
from notifier import get_chat_ids

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

if not TOKEN or not CHAT_ID:
    print("ERRO: TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID precisam estar no .env")
    sys.exit(1)


async def main():
    bot = Bot(token=TOKEN)
    text = (
        "<b>[Teste] claude-status-bot</b>\n"
        "Configuração OK — o bot está funcionando."
    )
    failures = 0
    for chat_id in get_chat_ids():
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            print(f"Mensagem de teste enviada com sucesso para o chat {chat_id}!")
        except TelegramError as e:
            failures += 1
            print(f"ERRO ao enviar para o chat {chat_id}: {e}")

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
