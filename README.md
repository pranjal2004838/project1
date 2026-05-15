# Pranjal's AI Outreach Engine

A Streamlit-based local application with four tabs that eliminates wasted time in your outreach and discovery. No cold applying to portals. Only leads that pass a strict AI filter reach you.

## Features
- **Freelance Leads**: Scrapes Reddit, HN, IndieHackers for high-intent gigs.
- **Internship & Contract**: Finds small agencies and founders actively building.
- **Cold Email to Founders**: Finds tech founders globally for peer-to-peer emails.
- **Hyderabad Stealth Hunter**: Finds local startups not on traditional job boards.

## Setup
1. `python -m venv venv`
2. Activate your virtual environment (e.g., `.\venv\Scripts\activate`)
3. `pip install -r requirements.txt`
4. Copy your `GEMINI_API_KEY` and `GITHUB_TOKEN` to the `.env` file.

## Running the App
Run this command from the root directory:
```bash
streamlit run app.py
```

*(Note: The old `devpresence` folder is kept for legacy reference, but `app.py` is the new main application.)*
