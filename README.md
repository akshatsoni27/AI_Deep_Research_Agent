# Signal Research Desk

![Signal Research Desk preview](image.png)

A Streamlit-powered multi-agent research system that turns an open question into a sourced research brief.

The pipeline uses four stages:

1. **Search Agent** finds recent sources with Tavily.
2. **Reader Agent** summarizes content gathered from the selected sources.
3. **Writer Agent** drafts a structured report.
4. **Critic Agent** reviews the report and identifies weaknesses.

## Features

- Concurrent web scraping with bounded requests and timeouts
- Character-encoding-safe HTML extraction
- Source, reading notes, report, and critique views
- Markdown report download
- Recent brief history during the current Streamlit session
- Stage and URL timing output for performance diagnosis

## Requirements

- Python 3.11 or newer
- A Tavily API key
- A Groq API key
- Internet access for model calls and source retrieval

## Local setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd MultiAgent-Project
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure local environment variables

Copy `.env.example` to `.env` and add your own keys.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Required variables:

```env
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

`.env` is ignored by Git. Never paste real keys into source code, README files, screenshots, issues, or commits.

## Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Open [share.streamlit.io](https://share.streamlit.io/) and select **New app**.
3. Choose your repository, branch, and set the main file to `app.py`.
4. Open **Advanced settings** and add the following secrets in TOML format:

```toml
TAVILY_API_KEY = "your_tavily_api_key"
GROQ_API_KEY = "your_groq_api_key"
GROQ_MODEL = "openai/gpt-oss-20b"
```

5. Deploy the app.

Do not upload `.env` or `.streamlit/secrets.toml` to GitHub. Streamlit Cloud secrets belong in the app's **Settings → Secrets** panel. The app reads Cloud secrets first when no matching local environment variable is present.

The deployment entry point is:

```text
app.py
```

## Run locally

```bash
python -m streamlit run app.py
```

Then open the local URL printed by Streamlit, usually `http://localhost:8501`.

To run the command-line pipeline directly:

```bash
python Pipeline.py
```

## Project structure

```text
.
├── app.py             # Streamlit frontend
├── Pipeline.py        # Four-stage research workflow
├── Agents.py          # LangChain agents and writer/critic chains
├── tools.py           # Tavily search and concurrent web scraping tools
├── config.py          # Local .env and Streamlit Cloud secret loader
├── requirements.txt   # Python dependencies
├── .env.example       # Safe environment-variable template
└── .gitignore         # Secrets and generated-file exclusions
```

## Security notes

- Keep `.env` local and verify it is ignored before committing.
- Rotate any API key that has been exposed publicly.
- Treat scraped web content as untrusted input.
- Do not commit `.venv`, caches, logs, generated reports, or Streamlit secrets.

## Troubleshooting

### `ImportError: cannot import name 'create_agent'`

Run Streamlit with the same Python interpreter used to install the dependencies:

```powershell
& ".\.venv\Scripts\python.exe" -m streamlit run app.py
```

### Groq rate limits

The model provider may enforce token-per-minute or token-per-day limits. Wait for the quota window to reset, use a model with available quota, or configure another model through `GROQ_MODEL`.

### Scraping failures

Some websites reject automated requests or require JavaScript. The pipeline records individual URL failures and continues with the remaining sources.
