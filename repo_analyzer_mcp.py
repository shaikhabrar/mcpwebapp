# repo_analyzer_mcp.py
import logging
import base64
import requests
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)

# Create MCP server
mcp = FastMCP("repo-analyzer")

def fetch_github_readme(repo_url: str) -> str:
    """
    Fetch README.md from a GitHub repo using GitHub API.
    If you have a GITHUB_TOKEN env var, it will be used for higher rate limits.
    """
    try:
        github_token = None
        import os
        github_token = os.environ.get("GITHUB_TOKEN")
        parts = repo_url.rstrip("/").split("/")
        user, repo = parts[-2], parts[-1]
        api_url = f"https://api.github.com/repos/{user}/{repo}/contents/README.md"
        headers = {}
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        resp = requests.get(api_url, headers=headers)
        if resp.status_code == 200:
            content = resp.json().get("content", "")
            return base64.b64decode(content).decode("utf-8")
        return f"Could not fetch README.md (status {resp.status_code})"
    except Exception as e:
        return f"Error fetching repo: {e}"

def ollama_chat(prompt: str, model: str = "mistral"):
    """
    Simple Ollama request (stream parsing).
    """
    url = "http://localhost:11434/api/generate"
    resp = requests.post(url, json={"model": model, "prompt": prompt}, stream=True, timeout=120)
    text = ""
    for line in resp.iter_lines():
        if line:
            data = line.decode("utf-8")
            # Ollama streams JSONL lines; crude extraction:
            if '"response":' in data:
                try:
                    text += data.split('"response":"', 1)[1].rsplit('"', 1)[0]
                except Exception:
                    text += data
    return text

# Expose analyzation via MCP tool
@mcp.tool()
def analyze_repo(repo_url: str, question: str = "") -> str:
    """
    MCP tool: fetch README and ask Mistral to analyze repo and answer the question.
    Returns the model text.
    """
    readme = fetch_github_readme(repo_url)
    if "Error" in readme or "Could not" in readme:
        return readme

    prompt = f"""
You are analyzing a GitHub repository. The user asks:
{question}

README content:
{readme}

Please:
1) Briefly summarize what the project is and does.
2) Explain main components and how the project flows.
3) Answer the user's question (if any).
"""
    return ollama_chat(prompt, "mistral")

if __name__ == "__main__":
    print("🚀 Repo Analyzer MCP server is starting (mcp) ...")
    mcp.run()
