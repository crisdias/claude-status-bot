import asyncio
import os
import logging
import sys

from dotenv import load_dotenv

from state import load_state, save_state
from rss_monitor import fetch_incidents
from notifier import send_new_incident, send_update

load_dotenv()

POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL_SECONDS", 300))
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _validate() -> None:
    errors: list[str] = []
    if not BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN não configurado")
    if not CHAT_ID:
        errors.append("TELEGRAM_CHAT_ID não configurado")
    if errors:
        for e in errors:
            logging.error(e)
        sys.exit(1)


async def main() -> None:
    _validate()
    state = load_state()
    first_run = not state

    if first_run:
        logging.info("Primeira execução — populando estado sem notificar")

    while True:
        try:
            incidents = await fetch_incidents()

            if first_run:
                for inc in incidents:
                    state[inc.guid] = len(inc.updates)
                save_state(state)
                first_run = False
                logging.info("Estado inicial salvo — %d incidentes monitorados", len(state))
            else:
                for inc in incidents:
                    guid = inc.guid
                    curr = len(inc.updates)
                    prev = state.get(guid, 0)

                    if guid not in state:
                        state[guid] = curr
                        await send_new_incident(inc)
                    elif curr > prev:
                        state[guid] = curr
                        await send_update(inc)

                save_state(state)

        except Exception as exc:
            logging.error("Erro no ciclo de polling: %s", exc)

        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
