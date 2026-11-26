"""Avisos de erro no ntfy.

Um `logging.Handler` que publica todo registro de nível ERROR ou acima no
tópico de erros do ntfy. Mensagens repetidas são agrupadas: no máximo um
aviso por mensagem a cada `NTFY_DEDUP_SECONDS` (padrão: 1 h), para que uma
falha que se repete a cada ciclo de polling não inunde o celular.
"""

import logging
import os
import time

import httpx

NTFY_DEFAULT_URL = "https://alertas.netcris.com.br/erros"
SOURCE = "claude-status-bot"


class NtfyHandler(logging.Handler):
    def __init__(self, url: str, token: str, dedup_seconds: int) -> None:
        super().__init__(level=logging.ERROR)
        self._url = url
        self._token = token
        self._dedup = dedup_seconds
        self._last_sent: dict[str, float] = {}

    def emit(self, record: logging.LogRecord) -> None:
        if getattr(record, "skip_ntfy", False):
            return
        try:
            message = self.format(record)
            key = record.getMessage()[:200]
            now = time.monotonic()
            last = self._last_sent.get(key)
            if last is not None and now - last < self._dedup:
                return
            self._last_sent[key] = now

            headers = {
                "Title": f"{SOURCE}: {record.levelname.lower()}",
                "Tags": "warning",
                "Priority": "high" if record.levelno >= logging.CRITICAL else "default",
                "User-Agent": f"{SOURCE}/1.0",
            }
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"
            resp = httpx.post(
                self._url,
                content=message.encode("utf-8"),
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
        except Exception as exc:  # o aviso nunca pode derrubar o bot
            logging.getLogger(__name__).warning(
                "Falha ao avisar no ntfy: %s", exc, extra={"skip_ntfy": True}
            )


def setup_ntfy(filters: list[logging.Filter]) -> None:
    """Liga o aviso no ntfy se `NTFY_TOKEN` estiver configurado."""
    token = os.environ.get("NTFY_TOKEN", "")
    if not token:
        logging.info("NTFY_TOKEN não configurado — avisos de erro no ntfy desligados")
        return
    url = os.environ.get("NTFY_URL", "") or NTFY_DEFAULT_URL
    dedup = int(os.environ.get("NTFY_DEDUP_SECONDS", 3600))
    handler = NtfyHandler(url, token, dedup)
    handler.setFormatter(logging.Formatter("%(message)s"))
    for f in filters:
        handler.addFilter(f)
    logging.getLogger().addHandler(handler)
    logging.info("Avisos de erro no ntfy ligados (%s)", url)
