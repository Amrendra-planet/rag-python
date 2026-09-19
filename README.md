# Operational Runbook AI Agent — Assessment Prototype

## Important dataset note
The original assessment PDF describes 12 runbooks but the runbook files were not supplied with the PDF available to us. Therefore, this repository contains 12 clearly labeled **sample runbooks** created to reproduce the assessment scenario. Replace the files in `runbooks/` with the official assessment runbooks if the recruiter provides them.

## What this project demonstrates
- Python implementation of `answer_question(question)`
- Retrieval over operational runbooks
- LLM-based grounded answer generation
- Citation validation
- Explicit `no_match` behavior
- Evaluation harness that distinguishes right citation, wrong citation, correct no-match, and incorrect no-match

## Setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add your OpenAI API key.

```text
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5-mini
```

Never commit `.env`.

## Run the evaluation

```bash
python tests/evaluation.py
```

## Run interactively

```bash
python main.py
```

## Architecture

Question -> retrieval -> top candidate runbooks -> LLM grounding/verification -> structured JSON answer.

Hybrid retrieval is intentionally simple in this starter implementation: lexical matching plus phrase bonuses. In a production implementation, this can be upgraded to embedding/vector retrieval plus lexical filtering and reranking.

## Interview explanation

The important design decision is to avoid blindly citing the closest semantic match. The corpus contains near-duplicate documents, so retrieval is only candidate generation. The LLM performs a second grounding step and is instructed to return `no_match` when evidence is insufficient.

## Security

API keys are loaded from environment variables and are not stored in source code.
# rag-python
