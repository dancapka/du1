"""
Ukázka: Python skript, který zavolá LLM API (OpenAI),
poskytne mu nástroj (výpočetní funkci) a vrátí výsledek zpět LLM
pro finální odpověď.

Spuštění:
    pip install openai python-dotenv
    python tool_use.py

API klíč se načítá z lokálního souboru .env (klíč OPENAI_API_KEY).
"""

import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = "gpt-4o-mini"


def calculate(expression: str) -> str:
    """Jednoduchá výpočetní funkce – vyhodnotí aritmetický výraz."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "Chyba: nepovolené znaky ve výrazu."
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Chyba při výpočtu: {e}"


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
    }
]


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
                print(f"[LLM volá nástroj] {call.function.name}({args})")
                if call.function.name == "calculate":
                    result = calculate(args["expression"])
                else:
                    result = "Neznámý nástroj."
                print(f"[Výsledek nástroje] {result}")
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
    otazka = "Kolik je (128 * 4) + 12? Použij nástroj na výpočet."
    print(f"Uživatel: {otazka}\n")
    odpoved = run(otazka)
    print(f"\nLLM: {odpoved}")
