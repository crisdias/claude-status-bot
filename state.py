import json
import os
import logging

STATE_FILE = os.environ.get("STATE_FILE", "state.json")

def load_state() -> dict[str, int]:
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        logging.warning("state.json corrompido, recriando")
        return {}

def save_state(state: dict[str, int]) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    logging.debug("Estado salvo (%d incidentes)", len(state))
