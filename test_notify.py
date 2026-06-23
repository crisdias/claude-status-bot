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
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="HTML", disable_web_page_preview=True)
        print("Mensagem de teste enviada com sucesso!")
    except TelegramError as e:
        print(f"ERRO ao enviar: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
