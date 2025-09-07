# SimplePlayground

A tiny Streamlit app to quickly try prompts across chat endpoints. Point it at any provider or self‑hosted/proxy service that speaks a Chat Completions–style API, tweak parameters, and export conversations.

## Features

- Provider‑agnostic: set any Base URL that exposes a `/v1` Chat Completions‑style API
- Model parameters: temperature, max_tokens (default 1024), top_p, frequency_penalty, presence_penalty
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
	- API Token: your provider key/token
	- Base URL: either check “Use sample base URL (/v1)” to use `http://localhost:11434/v1`, or provide your own (e.g., `https://your-provider.example.com/v1`)

2. Enter a model name (free text) and tweak parameters.

3. Type messages in the chat box; responses stream in. You can delete individual messages.

4. Export the conversation as JSON or TXT when you’re done.

## Provider notes

This app targets Chat Completions–style APIs. To use it, provide:

- A valid API token for your service
- A Base URL that exposes a `/v1` Chat Completions endpoint
- A model identifier your service recognizes (free‑text input)

Examples:

- Local runtime: `http://localhost:11434/v1`
- Hosted service: `https://your-provider.example.com/v1`

Note: If your provider requires non‑standard headers or routes, place a proxy in front that normalizes requests to a common Chat Completions shape.

## Troubleshooting

- 401/403 Unauthorized: Check your API token and whether the Base URL expects a different key or header format.
- 404 Not Found: Verify the Base URL points to an OpenAI‑compatible path (commonly ends with `/v1`).
- 429 Rate limit: Reduce request frequency or adjust your provider limits.
- AttributeError/TypeError around the SDK or `chat.completions`: Ensure the installed `openai` package is up to date (`pip install -U openai`).
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
