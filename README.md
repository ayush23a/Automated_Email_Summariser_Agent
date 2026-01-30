# 📧 Daily Email Summarizer Agent

A Production-Grade AI Agent built with **LangGraph** that fetches your emails, analyzes them using **Gemini** or **Groq** (Llama 3), and creates a beautifully formatted summary draft in your Gmail every morning.

![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-blue)
![Gemini](https://img.shields.io/badge/AI-Gemini%20%2F%20Groq-orange)
![Gmail](https://img.shields.io/badge/Integration-Gmail%20API-red)

## ✨ Features

- **Daily Cron Schedule**: Runs automatically at 8 AM IST (configurable).
- **Smart Analysis**: Extracts key points, categorizes emails, and assigns importance scores (1-5).
- **Category Sorting**: Groups emails by *Job Updates, Careers, Finance, Marketing, Social, System*, etc.
- **HTML Parsing**: Robustly handles marketing/newsletter emails by stripping HTML.
- **Rate Limiting**: Configurable delays and fetch limits to respect free tier API quotas.
- **Gmail Draft**: Creates a ready-to-send draft instead of auto-sending (Safety First).

## 🛠️ Tech Stack

- **Orchestration**: `langgraph`
- **LLM Framework**: `langchain`
- **Models**: Google Gemini 1.5 Flash / Groq Llama 3
- **Validation**: `pydantic`
- **Scheduler**: GitHub Actions

## 🚀 Setup Guide

### 1. Google Cloud Configuration
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable the **Gmail API**.
3. Configure **OAuth Consent Screen** (External, add your email to *Test Users*).
4. Create **OAuth Client ID** (Desktop App).
5. Download the JSON credential, rename to `credentials.json`, and place in project root.

### 2. Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration (.env)
Copy `.env.example` to `.env` and configure:
```ini
# AI Provider (gemini or groq)
MODEL_PROVIDER=groq
GROQ_API_KEY=gsk_...
# OR
# MODEL_PROVIDER=gemini
# GOOGLE_API_KEY=AIza...

# Settings
MAX_EMAILS_TO_FETCH=50   # 0 for unlimited
API_DELAY_SECONDS=2.0    # Rate limiting delay
```

### 4. Authentication (First Run)
Run locally once to generate `token.json`:
```bash
python main.py
```
*A browser window will open. Login with your Google account and click Allow.*

## 🤖 Deployment (GitHub Actions)

This repo includes a workflow to run the agent daily for free using GitHub Actions.

1. Push code to GitHub.
2. Go to **Settings > Secrets > Actions**.
3. Add the following repository secrets:
    - `GMAIL_CREDENTIALS_JSON`: Content of `credentials.json`
    - `GMAIL_TOKEN_JSON`: Content of `token.json`
    - `GROQ_API_KEY` (or `GOOGLE_API_KEY`)

The agent will now run automatically every day at 8:00 AM IST!

## ⚙️ Customization

- **Change Schedule**: Edit `.github/workflows/daily_summary.yml` (Cron syntax).
- **Adjust Limits**: implementation logic is in `src/nodes/fetch.py`.
- **Modify Prompt**: Edit `src/nodes/analyze.py`.

## 📄 License
MIT License
