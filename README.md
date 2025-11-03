# Transfer Assistant — DVC → UC (LLM-centric)
This repository contains an assistant that helps Diablo Valley College (DVC) students plan UC transfer preparation for a few UC campuses (UCB, UCD, UCSD). The agent parses free-form user queries, maps DVC courses to UC requirements, and shows remaining suggested DVC courses.

## Features
- Single-turn LLM parsing with deterministic fallbacks for safety.
- Multi-campus support (UC Berkeley, UC Davis, UC San Diego).
- Category filtering (major preparation, breadth/GE, math, science, CS).
- Interactive CLI with session-state (completed courses, domains, categories).
- Plain deterministic formatter and LLM-based pretty formatter.

## Contents
- `src/ai_agent.py`: main CLI program and parsing/filtering logic.
- `data/`: example data and logs. Place campus JSON files here (or use `agreements_25-26/`).
- `agreements_25-26/`: campus mapping JSONs included with the repo.

## Quick start

### Prerequisites
- Python 3.10+
- A Python virtual environment (recommended)
- An OpenAI-compatible API key stored in a `.env` file as `OPENAI_API_KEY` if you want LLM parsing/formatting.

## Data & logs
- Logs are written to `data/conversation_log.csv` and `data/user_log.jsonl`.
- Campus mapping JSON files are loaded from `data/uc*.json` and `agreements_25-26/*.json`.

## Development notes
- Parser output includes `matched_texts` and `confidence` fields to aid debugging and safe auto-apply behavior.
- Firebase frontend is in progress

## License
- See `LICENSE` in the repository root.

