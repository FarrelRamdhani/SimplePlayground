# SimplePlayground

A tiny Streamlit app to quickly try prompts across OpenAI‑compatible chat endpoints. Point it at OpenAI or any self‑hosted/proxy service that speaks the OpenAI Chat Completions API, tweak parameters, and export conversations.

## Features

- OpenAI‑compatible endpoint support (configurable Base URL in the sidebar)
- Model parameters: temperature, max_tokens, top_p, frequency_penalty, presence_penalty
- System prompt input for role/behavior
- Editable chat history with per‑message delete
- Export chat as JSON or plain text
- Simple, single‑file app (`main.py`)

## Requirements

- Python 3.9+ (3.10+ recommended)
- Packages in `requirements.txt`

## Quick start (Windows PowerShell)

1. Create and activate a virtual environment (optional but recommended):

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
streamlit run main.py
```

Streamlit will print a local URL (usually <http://localhost:8501>). Open it in your browser.

### Optional: Use a virtual environment

Although optional, using a virtual environment keeps your global Python clean:

```powershell
# Create a venv in a folder named ".venv" (preferred)
py -m venv .venv

# OR create it as "venv" (also common)
py -m venv venv

# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1
# or
.\venv\Scripts\Activate.ps1

# Deactivate when done
deactivate
```

If PowerShell blocks activation due to script policies, you can temporarily allow it for the current session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Usage

1. In the sidebar, configure your API details:
	- API Token: your provider key (e.g., OpenAI key starting with `sk-...`)
	- Base URL: either check “Use OpenAI default URL” or provide a custom base (e.g., a proxy)

2. Choose a model and tweak parameters.

3. Type messages in the chat box; responses stream in. You can delete individual messages.

4. Export the conversation as JSON or TXT when you’re done.

## Provider notes

This app uses the OpenAI Python SDK (v1.x) and the Chat Completions API path. If your service is truly OpenAI‑compatible, it should work by supplying:

- A valid API key for your service
- The correct Base URL for the Chat Completions endpoint
- A model name your service recognizes

Examples:

- OpenAI: Base URL `https://api.openai.com/v1` with your OpenAI API key
- Proxies / self‑hosted: Use the URL your proxy exposes (make sure it forwards to an OpenAI‑compatible Chat Completions API)

Note: Some providers mimic the API but require provider‑specific headers or paths. If so, ensure your proxy normalizes them to standard OpenAI headers/paths.

## Troubleshooting

- 401/403 Unauthorized: Check your API token and whether the Base URL expects a different key or header format.
- 404 Not Found: Verify the Base URL points to an OpenAI‑compatible path (commonly ends with `/v1`).
- 429 Rate limit: Reduce request frequency or adjust your provider limits.
- AttributeError/TypeError around `openai` or `chat.completions`: Ensure you’re on OpenAI Python SDK v1.x (`pip install -U openai`).
- Streamlit not starting on port 8501: Another process may be using the port. Close the other process or run `streamlit run main.py --server.port 8502`.

## Project structure

```text
.
├─ main.py              # Streamlit app
├─ requirements.txt     # Python dependencies
└─ LICENSE              # Project license
```

## License

This project is released under the MIT License. See `LICENSE` for details.
