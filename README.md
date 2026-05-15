# DevPresence

A Python-based CLI + dashboard application to market yourself as a freelance developer. 
It scans platforms (Reddit, LinkedIn, Discord, Slack) for opportunities and helps you respond using Gemini Gemini.

## Features
- Scalable platform scanners (Reddit integrated, more to add)
- Gemini Gemini AI persona building
- Duplicate prevention (SQLite / SQLAlchemy)
- Streamlit Web Dashboard
- Job scheduling (APScheduler)

## Setup
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in credentials.
5. `python devpresence/main.py --init`
6. `streamlit run devpresence/dashboard.py`
