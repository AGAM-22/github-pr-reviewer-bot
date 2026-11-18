# 🤖 Automated GitHub Pull Request Reviewer Bot

Welcome! If you are a beginner or a fresher exploring AI and backend automation, this README is written exactly for you. 

## 🌟 What is this project?
Imagine you are working on a team, and every time someone writes new code (a Pull Request), a senior developer has to read it to find bugs. 
This project automates that job! It is an AI bot that acts like a senior developer. Whenever you push new code to GitHub, this bot instantly reads it, uses **Google Gemini AI** to find bugs or security issues, and automatically posts a review comment on your GitHub Pull Request.

## ✨ How It Works (The Flow)
1. **You push code:** You create a Pull Request on GitHub.
2. **GitHub shouts out (Webhook):** GitHub sends a real-time signal (webhook) to our Python backend saying, "Hey, new code is here!"
3. **Backend fetches the code:** Our FastAPI server takes that signal and asks GitHub for the exact lines of code that were changed (`git diff`).
4. **AI does the magic:** We send this code to **Google Gemini 3.8 Flash**. The AI reads it and writes a detailed review.
5. **Auto-Comment:** The backend takes the AI's review and posts it back to your GitHub PR as a comment.

## 🛠️ Tech Stack Used
* **Python & FastAPI:** The engine running our backend server.
* **Google Gemini 3.8 Flash:** The AI brain that reviews the code.
* **ngrok:** A tool to connect our local laptop server to the live internet so GitHub can talk to it.
* **GitHub Webhooks & REST API:** To track events and post comments.

---

## 🚀 Step-by-Step Beginner's Setup Guide

Do you want to run this on your own laptop? Follow these steps exactly:

### Step 1: Get the Code
First, download this project to your computer. Open your terminal and run:
```bash
git clone [https://github.com/AGAM-22/github-pr-reviewer-bot.git](https://github.com/AGAM-22/github-pr-reviewer-bot.git)
cd github-pr-reviewer-bot
```

### Step 2: Create a Safe Environment
We use a "Virtual Environment" so the libraries installed for this project don't mess up other Python projects on your laptop.
```bash
python -m venv venv
```
Activate it:
* **Windows:** `venv\Scripts\activate`
* **Mac/Linux:** `source venv/bin/activate`

### Step 3: Install Required Tools
Now, install FastAPI, Uvicorn, and other required Python libraries:
```bash
pip install -r requirements.txt
```

### Step 4: Setup Your Secret API Keys
Your bot needs passwords (API keys) to talk to Google AI and GitHub. We keep these safe in a hidden `.env` file.
1. Copy the template file: `cp .env_example .env`
2. Open the new `.env` file in your code editor.
3. You need to fill in these 3 things:
   * `GEMINI_API_KEY`: Go to **Google AI Studio**, sign in, and create a free API key. Paste it here.
   * `GITHUB_TOKEN`: Go to your GitHub Profile -> Settings -> Developer Settings -> Personal Access Tokens (Classic). Generate a new token with `repo` permissions. Paste it here.
   * `WEBHOOK_SECRET`: This is just a password you make up. Type any random word (e.g., `mysecret123`).

### Step 5: Start Your Local Server
Run this command to start your FastAPI backend:
```bash
uvicorn main:app --reload --port 8000
```
*(Your backend is now running on `http://localhost:8000`, but GitHub cannot see your localhost yet.)*

### Step 6: Connect to the Internet using ngrok
Open a **new, second terminal window** (leave the first one running) and use ngrok to create a public link for your local server:
```bash
ngrok http 8000
```
Copy the `Forwarding` URL it gives you. It will look something like: `https://abcd-12-34-56.ngrok-free.app`

### Step 7: Tell GitHub Where to Send the Data (Webhook)
1. Go to your GitHub Repository online.
2. Click **Settings** -> **Webhooks** -> **Add webhook**.
3. **Payload URL:** Paste your ngrok URL and add `/webhook` at the end (e.g., `https://abcd...ngrok-free.app/webhook`).
4. **Content type:** Select `application/json`.
5. **Secret:** Type the exact same `WEBHOOK_SECRET` you made up in Step 4.
6. Under events, select **Let me select individual events** and check only **Pull requests**.
7. Click **Add webhook**.

### 🎉 You are Done! 
Now, make a change in a separate branch, open a Pull Request, and watch the AI review your code in seconds!