"""
Ukázka: Python skript, který zavolá LLM API (OpenAI),
poskytne mu dva nástroje — výpočetní funkci a webové vyhledávání (DDGS) —
a výsledky vrátí zpět modelu pro finální odpověď.

Spuštění:
    uv sync
    echo "OPENAI_API_KEY=sk-..." > .env
    uv run python tool_use.py
"""

import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from ddgs import DDGS

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = "gpt-5.4-nano"


def calculate(expression: str) -> str:
    """Vyhodnotí aritmetický výraz."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "Chyba: nepovolené znaky ve výrazu."
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Chyba při výpočtu: {e}"


def web_search(query: str, max_results: int = 5) -> str:
    """Vyhledá dotaz přes DuckDuckGo (DDGS) a vrátí top výsledky jako JSON."""
    try:
        with DDGS() as ddgs:
            hits = list(ddgs.text(query, max_results=max_results))
        if not hits:
            return "Žádné výsledky."
        trimmed = [
            {
                "title": h.get("title"),
                "href": h.get("href"),
                "snippet": h.get("body"),
            }
            for h in hits
        ]
        return json.dumps(trimmed, ensure_ascii=False)
    except Exception as e:
        return f"Chyba vyhledávání: {e}"


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Vyhodnotí aritmetický výraz a vrátí číselný výsledek.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Aritmetický výraz, např. '(12 + 7) * 3'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Vyhledá aktuální informace na webu přes DuckDuckGo. "
                "Použij pro dotazy na fakta, zprávy, aktuality, lidi, produkty apod."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Vyhledávací dotaz.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Počet výsledků (default 5).",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


TOOL_IMPL = {
    "calculate": lambda args: calculate(args["expression"]),
    "web_search": lambda args: web_search(
        args["query"], args.get("max_results", 5)
    ),
}


def run(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                args = json.loads(call.function.arguments)
                name = call.function.name
                print(f"[LLM volá nástroj] {name}({args})")
                impl = TOOL_IMPL.get(name)
                result = impl(args) if impl else "Neznámý nástroj."
                preview = result if len(result) < 200 else result[:200] + "…"
                print(f"[Výsledek nástroje] {preview}")
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result,
                    }
                )
            continue

        return msg.content or ""


if __name__ == "__main__":
    otazka = (
        "Kdo je aktuálním prezidentem České republiky a kolik je (128 * 4) + 12? "
        "Použij nástroje – web pro prezidenta, kalkulačku pro výpočet."
    )
    print(f"Uživatel: {otazka}\n")
    odpoved = run(otazka)
    print(f"\nLLM: {odpoved}")
