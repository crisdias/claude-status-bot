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


RESOLVED_STATUSES = {"Resolved"}


def _emoji(incident: Incident, is_new: bool) -> str:
    latest = incident.updates[0]
    if latest.status in RESOLVED_STATUSES:
        return "\u2705"
    return "\u274c" if is_new else "\u2757"


def _format(incident: Incident, emoji: str) -> str:
    latest = incident.updates[0]
    return (
        f"{emoji} <b>{incident.title}</b>\n"
        f"<b>{latest.status}</b> \u2014 {latest.message}\n"
        f"{latest.timestamp}\n"
        f"{incident.link}"
    )


async def send_new_incident(incident: Incident) -> None:
    text = _format(incident, _emoji(incident, is_new=True))
    try:
        await _bot().send_message(chat_id=_chat_id(), text=text, parse_mode="HTML", disable_web_page_preview=True)
        logging.info("Novo incidente notificado: %s", incident.guid)
    except TelegramError as e:
        logging.error("Falha ao notificar novo incidente: %s", e)


async def send_update(incident: Incident) -> None:
    text = _format(incident, _emoji(incident, is_new=False))
    try:
        await _bot().send_message(chat_id=_chat_id(), text=text, parse_mode="HTML", disable_web_page_preview=True)
        logging.info("Atualização notificada: %s", incident.guid)
    except TelegramError as e:
        logging.error("Falha ao notificar atualização: %s", e)
