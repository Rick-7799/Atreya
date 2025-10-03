# Atreya — Personalized Health Recommender

> **Demo / educational project** inspired by Smart India Hackathon 2023 & Social Summer of Code Season 3.
> Uses knowledge graphs to map Ayurvedic herbs and generate **gentle, non‑medical** wellness suggestions.
> **Not medical advice** — always consult a qualified professional.

## Tech
- **LangChain**: prompt/chain orchestration for LLM reasoning.
- **Neo4j**: knowledge graph.
- **FastAPI**: backend API that queries Neo4j and composes prompts for LangChain.


### 1) Make a new Python space
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2) Install packages
```bash
pip install -r requirements.txt
```

### 3) Load the graph
```bash
python graph/load_data.py
```
### 4) Start the backend
```bash
uvicorn --app-dir backend main:app --reload --env-file .env
```
- It will print something like: `http://127.0.0.1:8000`
- Open `http://127.0.0.1:8000/docs` to see the API.

### 5) Start the front-end
In a **new** terminal (keep backend running):
```bash
streamlit run streamlit_app/app.py
```
- Streamlit page opens in your browser.
- Type symptoms/lifestyle → press **Get Recommendations**.

---

## Safety
- All outputs are **suggestions** for discussion with a doctor.
---
