import os
import logging

from telegram import Bot
from telegram.error import TelegramError

from rss_monitor import Incident
from translator import translate


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


def _format(incident: Incident, emoji: str, message: str, status: str | None = None) -> str:
    latest = incident.updates[0]
    label = status or latest.status
    return (
        f"{emoji} <b>{incident.title}</b>\n"
        f"<b>{label}</b> \u2014 {message}\n"
        f"{latest.timestamp}\n"
        f"{incident.link}"
    )


async def _send(incident: Incident, emoji: str, log_action: str) -> None:
    latest = incident.updates[0]
    msg = await translate(latest.message)
    text = _format(incident, emoji, msg)
    try:
        await _bot().send_message(chat_id=_chat_id(), text=text, parse_mode="HTML", disable_web_page_preview=True)
        logging.info("%s notificado: %s", log_action, incident.guid)
    except TelegramError as e:
        logging.error("Falha ao notificar %s: %s", log_action, e)


async def send_new_incident(incident: Incident) -> None:
    await _send(incident, _emoji(incident, is_new=True), "Novo incidente")


async def send_update(incident: Incident) -> None:
    await _send(incident, _emoji(incident, is_new=False), "Atualização")
