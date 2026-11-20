import asyncio
import os
import random
import httpx
from fastapi import BackgroundTasks, FastAPI, Request
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

ai_client = genai.Client(api_key=GEMINI_API_KEY)
app = FastAPI()

GITHUB_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}

RETRYABLE_CODES = {429, 500, 502, 503, 504}


@app.get("/")
def home():
    return {"message": "PR Reviewer Bot is live"}


async def process_pr_review(repo_full_name: str, pr_number: int, pr_title: str):
    try:
        print(f"[+] PR #{pr_number} ka diff fetch kar raha hoon...", flush=True)
        diff_text = await get_pr_diff(repo_full_name, pr_number)

        print("[+] AI se code review generate karwa raha hoon...", flush=True)
        ai_feedback = await review_code_with_ai(pr_title, diff_text)

        final_comment = f"## Automated AI Code Review\n\n{ai_feedback}"
        await post_github_comment(repo_full_name, pr_number, final_comment)
    except Exception as exc:
        print(f"[X] PR #{pr_number} review fail hua: {type(exc).__name__}: {exc}", flush=True)


@app.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    event_name = request.headers.get("X-GitHub-Event", "unknown_event")
    payload = await request.json()

    if event_name == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize", "reopened"]:
            repo_full_name = payload["repository"]["full_name"]
            pr_number = payload["pull_request"]["number"]
            pr_title = payload["pull_request"]["title"]

            # Kaam background mein bhejo aur turant response return karo
            background_tasks.add_task(process_pr_review, repo_full_name, pr_number, pr_title)
            print(f"[>] PR #{pr_number} ({action}) background task mein queue ho gaya.", flush=True)

    return {"status": "success", "event": event_name}


async def get_pr_diff(repo: str, pr_number: int) -> str:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {**GITHUB_HEADERS, "Accept": "application/vnd.github.v3.diff"}
    timeout = httpx.Timeout(connect=10.0, read=25.0, write=10.0, pool=10.0)

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        print(f"[+] GitHub Diff API Status: {response.status_code}", flush=True)
        if response.status_code == 200:
            return response.text
        return ""


def _call_gemini_sync(prompt: str) -> str:
    response = ai_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return (response.text or "").strip()


async def review_code_with_ai(title: str, diff: str, max_attempts: int = 5) -> str:
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
    {diff[:2500]}
    ```
    """

    for attempt in range(1, max_attempts + 1):
        try:
            text = await asyncio.to_thread(_call_gemini_sync, prompt)
            if text:
                return text
            raise RuntimeError("Gemini ne empty response diya.")
        except APIError as err:
            code = getattr(err, "code", None)
            is_retryable = code in RETRYABLE_CODES or "UNAVAILABLE" in str(err).upper()
            if not is_retryable or attempt == max_attempts:
                raise
            wait_sec = (2.0 * (2 ** (attempt - 1))) + random.uniform(0.2, 0.8)
            print(f"[!] Gemini busy ({code}). Attempt {attempt}/{max_attempts}, {wait_sec:.1f}s baad retry...", flush=True)
            await asyncio.sleep(wait_sec)
        except Exception as err:
            if attempt == max_attempts:
                raise
            wait_sec = (2.0 * (2 ** (attempt - 1))) + random.uniform(0.2, 0.8)
            print(f"[!] Temporary error ({err}). Attempt {attempt}/{max_attempts}, {wait_sec:.1f}s baad retry...", flush=True)
            await asyncio.sleep(wait_sec)

    return "Review generate nahi ho paaya."


async def post_github_comment(repo: str, pr_number: int, message: str):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {**GITHUB_HEADERS, "Accept": "application/vnd.github+json"}
    timeout = httpx.Timeout(connect=10.0, read=25.0, write=10.0, pool=10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json={"body": message}, headers=headers)
        print(f"[+] GitHub Comment API Status: {response.status_code}", flush=True)
        if response.status_code >= 400:
            print(f"[!] GitHub Comment Error Body: {response.text}", flush=True)