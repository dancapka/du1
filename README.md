# LLM Tool Use — ukázkový skript

Python skript, který zavolá LLM API (OpenAI), poskytne mu výpočetní nástroj a
vrátí výsledek nástroje zpět modelu, aby LLM mohl formulovat finální odpověď.

## Co program dělá

1. Definuje lokální funkci `calculate(expression)` — bezpečně vyhodnotí
   aritmetický výraz.
2. Zaregistruje ji jako nástroj (`tools=[...]`) — OpenAI model dostane popis
   funkce a jejích parametrů.
3. Pošle dotaz modelu: *"Kolik je (128 * 4) + 12? Použij nástroj na výpočet."*
4. Ve smyčce zpracuje `tool_calls`:
   - model místo odpovědi požádá o zavolání `calculate`,
   - skript funkci spustí lokálně a výsledek pošle zpět jako `role: "tool"`,
   - model dostane výsledek a zformuluje finální větu.
5. Vypíše kroky a finální odpověď.

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
Uživatel: Kolik je (128 * 4) + 12? Použij nástroj na výpočet.

[LLM volá nástroj] calculate({'expression': '(128 * 4) + 12'})
[Výsledek nástroje] 524

LLM: Výsledek výrazu (128 * 4) + 12 je 524.
```
