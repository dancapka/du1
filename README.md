# LLM Tool Use — ukázkový skript

Python skript, který zavolá LLM API (OpenAI, model `gpt-5.4-nano`) a dá mu
k dispozici dva nástroje: **kalkulačku** a **webové vyhledávání přes DDGS**
(DuckDuckGo). Výsledky nástrojů se vracejí zpět modelu pro finální odpověď.

## Co program dělá

1. Definuje dvě lokální funkce:
   - `calculate(expression)` — bezpečně vyhodnotí aritmetický výraz.
   - `web_search(query)` — přes knihovnu `ddgs` vyhledá na DuckDuckGo
     a vrátí top výsledky (title, href, snippet) jako JSON.
2. Obě funkce zaregistruje jako nástroje (`tools=[...]`) s JSON schématem.
3. Pošle dotaz modelu — např. *"Kdo je aktuálním prezidentem ČR a kolik je
   (128 * 4) + 12?"*
4. Ve smyčce zpracuje `tool_calls`:
   - model si řekne o `web_search` / `calculate`,
   - skript funkci spustí lokálně a výsledek pošle zpět jako `role: "tool"`,
   - model výsledky zkombinuje a zformuluje finální větu.
5. Vypíše jednotlivé kroky i finální odpověď.

Tímto způsobem LLM sám nepočítá — rozhoduje, kdy delegovat práci na externí
funkci. Stejný princip stojí za agenty volajícími API, databáze apod.

## Spuštění (uv)

```bash
# instalace uv (jednorázově)
curl -LsSf https://astral.sh/uv/install.sh | sh

# závislosti se nainstalují automaticky z pyproject.toml / uv.lock
uv sync

# nastav API klíč
echo "OPENAI_API_KEY=sk-..." > .env

# spuštění
uv run python tool_use.py
```

## Soubory

- `tool_use.py` — hlavní skript s definicí nástroje a smyčkou tool-use.
- `pyproject.toml`, `uv.lock` — uv projekt a lockfile.
- `.env` — API klíč (gitignored).

## Ukázkový výstup

```
Uživatel: Kdo je aktuálním prezidentem ČR a kolik je (128 * 4) + 12?

[LLM volá nástroj] web_search({'query': 'aktuální prezident ČR', ...})
[Výsledek nástroje] [{"title": "Prezident ČR – Wikipedie", ...}, ...]
[LLM volá nástroj] calculate({'expression': '(128 * 4) + 12'})
[Výsledek nástroje] 524

LLM: Aktuální prezident ČR: Petr Pavel. (128 × 4) + 12 = 524.
```
