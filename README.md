# Autonomous Lead Engine

A daily autonomous sales engine that scrapes Google Maps, deduplicates data, scores leads, and uses a local LLM (Ollama) to generate outreach messages and a daily sales plan.

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- [Ollama](https://ollama.com/) installed and running locally.

### 2. Install Dependencies
Navigate to the `lead-engine` directory and install the required packages:

```bash
cd "Lead bot/lead-engine"
pip install -r requirements.txt
playwright install chromium
```

### 3. Setup Ollama
Make sure Ollama is running, then pull the required model (default is `llama3`):
```bash
ollama run llama3
```

## Running the Engine

### Manual Run
To execute the daily workflow (Scrape -> Process -> Score -> Generate Plan):
```bash
python3 scripts/runner.py
```
This will create a new Markdown file in the `outputs/` directory.

### View the Dashboard
To see the generated plans in a clean, local UI:
```bash
python3 app.py
```
Open your browser and navigate to `http://localhost:5000`.

## Configuration
Modify `config.json` to change target areas, search queries, or the Ollama endpoint:
- `search_queries`: List of queries for Google Maps.
- `high_value_areas`: Substrings of locations to boost scores.
- `high_value_categories`: Substrings of business categories to boost scores.
- `ollama_model`: The Ollama model to use.

## Automation (Cron Job)
To run this automatically every morning at 8:00 AM, set up a cron job.

1. Open your terminal and type `crontab -e`
2. Add the following line (update the path to match your system):
```bash
0 8 * * * cd /Users/barathkumar/Applications/CBK-apps/"Lead bot"/lead-engine && /path/to/your/python3 scripts/runner.py >> run.log 2>&1
```
