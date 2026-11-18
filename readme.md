# Automated GitHub Pull Request Reviewer Bot

An event-driven AI code review assistant built with **FastAPI**, **GitHub Webhooks**, and **Google Gemini 3.8 Flash**. Whenever a Pull Request is opened or updated, the bot automatically fetches the `git diff`, analyzes the changes for bugs, security vulnerabilities, and code quality issues, and posts a structured review comment directly on the PR.

## Architecture Flow
1. **GitHub Webhook** triggers on `pull_request` events (`opened`, `synchronize`, `reopened`).
2. **FastAPI Server** receives the webhook payload and fetches the raw code diff via the GitHub REST API.
3. **Gemini 3.8 Flash** evaluates the diff and generates a structured Markdown review (Summary, Bugs/Security Issues, Improvements).
4. **GitHub Comments API** posts the generated review directly onto the Pull Request thread.

## Tech Stack
- **Backend:** Python, FastAPI, Uvicorn, HTTPX
- **AI Engine:** Google GenAI SDK (`gemini-3.8-flash`)
- **Integrations:** GitHub REST API, GitHub Webhooks, ngrok

## Local Setup
1. Clone the repository and create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt