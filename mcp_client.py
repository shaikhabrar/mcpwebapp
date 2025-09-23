import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_mistral(question: str, repo_link: str = "") -> str:
    """
    Send a prompt to Mistral running in Ollama and get back a response.
    If repo_link is provided, include it in the question.
    """
    full_prompt = question
    if repo_link:
        full_prompt += f"\n\nThe GitHub repo is here: {repo_link}. Please analyze it and explain."

    response = requests.post(
        OLLAMA_URL,
        json={"model": "mistral", "prompt": full_prompt},
        stream=True
    )

    output = ""
    for line in response.iter_lines():
        if line:
            try:
                data = line.decode("utf-8")
                if '"response":' in data:
                    text_piece = data.split('"response":"')[1].split('"')[0]
                    output += text_piece
            except Exception:
                pass
    return output.strip()
