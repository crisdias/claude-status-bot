import os
import logging

from telegram import Bot
from telegram.error import TelegramError

from rss_monitor import Incident


_bot_instance = None


def _bot() -> Bot:
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    return _bot_instance


def _chat_id() -> str:
    return os.environ["TELEGRAM_CHAT_ID"]


def _format(incident: Incident, prefix: str) -> str:
    latest = incident.updates[0]
    return (
        f"<b>[{prefix}] {incident.title}</b>\n"
        f"<b>{latest.status}</b> — {latest.message}\n"
        f"{latest.timestamp}\n"
        f"{incident.link}"
    )


async def send_new_incident(incident: Incident) -> None:
    text = _format(incident, "Novo")
    try:
        await _bot().send_message(chat_id=_chat_id(), text=text, parse_mode="HTML", disable_web_page_preview=True)
        logging.info("Novo incidente notificado: %s", incident.guid)
    except TelegramError as e:
        logging.error("Falha ao notificar novo incidente: %s", e)


async def send_update(incident: Incident) -> None:
    text = _format(incident, "Atualização")
    try:
        await _bot().send_message(chat_id=_chat_id(), text=text, parse_mode="HTML", disable_web_page_preview=True)
        logging.info("Atualização notificada: %s", incident.guid)
    except TelegramError as e:
        logging.error("Falha ao notificar atualização: %s", e)
