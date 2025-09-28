import requests, json

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_mistral(question: str, repo_link: str = "") -> str:
    """
    Send a prompt to Mistral running in Ollama and get back a response.
    If repo_link is provided, include it as context, but do not force 'explain'.
    """
    if repo_link:
        full_prompt = f"You have access to this GitHub repo: {repo_link}.\n\nUser question: {question}"
    else:
        full_prompt = question

    response = requests.post(
        OLLAMA_URL,
        json={"model": "mistral", "prompt": full_prompt},
        stream=True
    )
    """Previos logic"""
    """if repo_link: full_prompt += f"The GitHub repo is here: {repo_link}. Please analyze it and explain." 
    response = requests.post( OLLAMA_URL, json={"model": "mistral", "prompt": full_prompt}, stream=True ) """


    output = ""
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    output += data["response"]
            except Exception:
                pass
    return output.strip()
