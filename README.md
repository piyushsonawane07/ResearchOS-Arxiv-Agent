## Research OS

A multi-agent research assistant that:
- finds relevant ArXiv papers,
- analyzes paper metadata,
- formats 
PA 7th Edition citations,
- provides a Streamlit UI to run the full flow.

<img width="1915" height="1104" alt="Screenshot 2026-01-20 at 3 37 04 PM" src="https://github.com/user-attachments/assets/0ae7cd4b-8603-4661-9643-e30cbcdcb771" />

## Requirements

- Python 3.10+
- Ollama running with the configured model in `main.py`

## Setup

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Streamlit app

```
streamlit run streamlit_app.py
```

## Run agents directly (optional)

```
python src/agents/researcher_agent.py
python src/agents/supervisor_agent.py
```

## Notes

- The formatter expects **paper-level metadata** (title, authors, published date, URL).
- The analyst outputs summary analytics plus ASCII charts.
