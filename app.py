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
    # Clear chat history on fresh visit
    session.pop("history", None)
    return render_template("index.html", started=started, pid_info=pid_info)

@app.route("/start_server", methods=["POST"])
def start_server():
    """Start MCP server"""
    global started, pid_info
    if not started:
        process = subprocess.Popen(["python", "repo_analyzer_mcp.py"])
        pid_info = process.pid
        started = True
    return redirect(url_for("index"))

@app.route("/ask", methods=["POST"])
def ask():
    """Submit first question + repo link, then redirect to chat page"""
    q = request.form["question"]
    repo = request.form["repo_link"]

    # First call with repo
    answer = ask_mistral(q, repo)
    if answer:
        answer = str(answer).replace("\\n", "\n")

    # Save conversation
    history = session.get("history", [])
    history.append((q, answer))
    session["history"] = history

    return redirect(url_for("chat"))

@app.route("/chat", methods=["GET", "POST"])
def chat():
    """Chat page (GET shows history, POST adds new Q/A then redirects)"""
    if request.method == "POST":
        q = request.form["question"]

        # Follow-up call without repo (Mistral keeps context internally)
        answer = ask_mistral(q)
        if answer:
            answer = str(answer).replace("\\n", "\n")

        history = session.get("history", [])
        history.append((q, answer))
        session["history"] = history

        return redirect(url_for("chat"))

    # GET → just show chat page
    return render_template("chat.html", history=session.get("history", []))

@app.route("/reset")
def reset():
    """Start fresh chat"""
    session.clear()
    return redirect(url_for("index"))

# ----------- RUN ------------

if __name__ == "__main__":
    app.run(debug=True)
