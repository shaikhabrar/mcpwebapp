from mcp_client import ask_mistral
from flask import Flask, render_template, request, redirect, url_for, session
import subprocess, os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # required for session

started = False
pid_info = None

# ----------- ROUTES ------------

@app.route("/")
def index():
    """Landing page: Start server or ask question"""
    # Clear chat history + repo on fresh visit
    session.pop("history", None)
    session.pop("repo_link", None)
    return render_template("index.html", started=started, pid_info=pid_info)

@app.route("/start_server", methods=["POST"])
def start_server():
    """Start MCP server"""
    global started, pid_info
    if not started:
        # Example: start your MCP server (repo_analyzer_mcp.py)
        process = subprocess.Popen(["python", "repo_analyzer_mcp.py"])
        pid_info = process.pid
        started = True
    return redirect(url_for("index"))

@app.route("/ask", methods=["POST"])
def ask():
    """Submit first question + repo link, then go to chat page"""
    q = request.form["question"]
    repo = request.form["repo_link"]

    # Save repo in session
    session["repo_link"] = repo

    # Call Mistral with repo
    answer = ask_mistral(q, repo)

    # Save conversation in session
    history = session.get("history", [])
    history.append((q, answer))
    session["history"] = history

    return render_template("chat.html", history=history)

@app.route("/chat", methods=["POST"])
def chat():
    """Submit follow-up question in chat"""
    q = request.form["question"]

    # Retrieve repo from session
    repo = session.get("repo_link", "")

    # Call Mistral with same repo
    answer = ask_mistral(q, repo)

    history = session.get("history", [])
    history.append((q, answer))
    session["history"] = history

    return render_template("chat.html", history=history)

# ----------- RUN ------------

if __name__ == "__main__":
    app.run(debug=True)
