# FieldMind — Enterprise Field Intelligence Agent

**Turning informal field reports into enterprise intelligence**

Enterprises operating in emerging markets often lose critical field intelligence because reports are informal, inconsistent, and hard to aggregate. Valuable operational signals stay trapped in fragmented WhatsApp messages, call notes, and ad-hoc updates. FieldMind converts noisy frontline reporting into structured, actionable enterprise insight.

## How it works

1. **Input**: Field agents submit informal reports in everyday language.
2. **Gemini Extraction**: Gemini transforms each report into structured JSON intelligence.
3. **Storage**: Structured intelligence is saved in SQLite for reliable retrieval.
4. **RAG Indexing**: Summaries are indexed in ChromaDB for context-aware reasoning.
5. **Dashboard**: Managers monitor trends, urgency, and sentiment in Streamlit.

## Tech stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Report submission, agent Q&A, dashboards |
| LLM Extraction | Google Gemini (gemini-2.0-flash) | Parse informal reports into structured data |
| Operational Database | SQLite | Persist extracted field intelligence |
| Retrieval Layer | ChromaDB | Vector indexing and report retrieval |
| Analytics | Pandas + Plotly | KPI metrics and visual insights |
| Config | python-dotenv | Secure `.env` key loading |

## How to run locally

1. `git clone <repo_url>`
2. `pip install -r requirements.txt`
3. Create `.env` with `GEMINI_API_KEY=your_key`
4. `python sample_data.py`
5. `streamlit run app.py`

## File structure

```text
FieldMind/
├── app.py
├── extractor.py
├── database.py
├── rag.py
├── sample_data.py
├── requirements.txt
├── .gitignore
└── README.md
```

Built for: **lablab.ai Transforming Enterprise Through AI Hackathon** and **AI Agent Olympics Hackathon**

Author: **Prince Nasamu Alhassan (Prince N. Alhassan), University of Ghana**
