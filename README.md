## Research OS

A multi-agent research assistant that:
- finds relevant ArXiv papers,
- analyzes paper metadata,
- formats PA 7th Edition citations,

  
<img width="1070" height="712" alt="Screenshot 2026-01-31 at 8 00 39 AM" src="https://github.com/user-attachments/assets/0757e8c7-0797-4767-9539-b74a6ced2b9e" />

## Requirements

- Python 3.10+
- Ollama running with the configured model in `main.py`

## Setup

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run CLI app

```
python cli.py
```

## Run agents directly (optional)

```
python src/agents/researcher_agent.py
python src/agents/supervisor_agent.py
```

## Notes

- The formatter expects **paper-level metadata** (title, authors, published date, URL).
- The analyst outputs summary analytics plus ASCII charts.
