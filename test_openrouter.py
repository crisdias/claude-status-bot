"""Testa tradução via OpenRouter.

Uso:
  .venv/bin/python test_openrouter.py
"""

import asyncio
from dotenv import load_dotenv
from translator import translate

load_dotenv()

TEXTS = [
    "We are currently investigating this issue.",
    "A fix has been implemented and we are monitoring the results.",
    "This incident has been resolved.",
]


async def main():
    print("Testando OpenRouter...")
    for t in TEXTS:
        r = await translate(t)
        ok = "\u2713" if r != t else "\u2717"
        print(f"  {ok} EN: {t}")
        print(f"    PT: {r}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
