# LLM Tool Use — ukázkový skript

Python skript, který zavolá LLM API (OpenAI), poskytne mu výpočetní nástroj a
vrátí výsledek nástroje zpět modelu, aby LLM mohl formulovat finální odpověď.

## Princip

1. Uživatel pošle dotaz modelu.
2. Model se rozhodne zavolat nástroj `calculate` (popsán v `tools`).
3. Skript nástroj lokálně spustí a výsledek pošle zpět modelu jako `tool` zprávu.
4. Model vrátí finální textovou odpověď.

## Spuštění

```bash
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-..." > .env
python tool_use.py
```

## Soubory

- `tool_use.py` — hlavní skript s definicí nástroje a smyčkou tool-use.
- `.env` — API klíč (gitignored).
- `requirements.txt` — závislosti.
