import os
import httpx
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from google import genai

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ai_client = genai.Client(api_key=GEMINI_API_KEY)
app = FastAPI()

GITHUB_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}

@app.get("/")
def home():
    return {"message": "PR Reviewer Bot is live"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    event_name = request.headers.get("X-GitHub-Event", "unknown_event")
    payload = await request.json()

    if event_name == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize", "reopened"]:
            repo_full_name = payload["repository"]["full_name"]
            pr_number = payload["pull_request"]["number"]
            pr_title = payload["pull_request"]["title"]
            
            print(f"[+] PR #{pr_number} ka diff fetch kar raha hoon...", flush=True)
            diff_text = await get_pr_diff(repo_full_name, pr_number)
            
            print("[+] AI se code review generate karwa raha hoon...", flush=True)
            ai_feedback = review_code_with_ai(pr_title, diff_text)
            
            final_comment = f"## Automated AI Code Review\n\n{ai_feedback}"
            await post_github_comment(repo_full_name, pr_number, final_comment)

    return {"status": "success", "event": event_name}

async def get_pr_diff(repo: str, pr_number: int) -> str:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {**GITHUB_HEADERS, "Accept": "application/vnd.github.v3.diff"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return ""

def review_code_with_ai(title: str, diff: str) -> str:
    if not diff.strip():
        return "Is PR mein koi code changes nahi mile."
        
    prompt = f"""
    You are an expert senior software engineer reviewing a GitHub Pull Request.
    PR Title: {title}
    
    Analyze the following git diff and provide a concise, actionable code review in Markdown:
    1. **Summary:** What this change does in 1-2 lines.
    2. **Bugs / Security Issues:** Flag any syntax errors, logic bugs, or exposed secrets/API keys. (If none, say "None found").
    3. **Improvements:** Suggest cleaner code, edge-case handling, or best practices.
    
    Git Diff:
    ```diff
    {diff[:6000]}
    ```
    """
    response = ai_client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt

    )
    return response.text

async def post_github_comment(repo: str, pr_number: int, message: str):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {**GITHUB_HEADERS, "Accept": "application/vnd.github+json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"body": message}, headers=headers)
        print(f"[+] GitHub Comment API Status: {response.status_code}", flush=True)