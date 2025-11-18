# License Finder App - Browser Automation

A Streamlit web application that uses Groq's browser automation API to find license information from web pages, including searching through nested links.

## Features

- 🤖 **Browser Automation**: Launches multiple browsers to search through pages
- 🔍 **Deep Search**: Follows nested links to find license information
- 📊 **Structured Output**: Extracts license type, URL, and confidence level
- 💾 **Export Results**: Download findings as JSON
- 📚 **URL History**: Quick access to recently analyzed URLs
- 🧠 **Transparent Process**: View browser automation reasoning and sessions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

Or enter it directly in the app sidebar.

### 3. Run the App

```bash
streamlit run license_finder_app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Enter a URL**: Paste the webpage URL where you want to find license information
2. **Select Model** (optional): Choose between:
   - `moonshotai/kimi-k2-instruct-0905` (default, fast)
   - `groq/compound-mini` (more thorough)
   - `groq/compound` (most comprehensive)
3. **Click "Find License Information"**: The app will:
   - Launch browser automation sessions
   - Search the main page and nested links
   - Extract license information
   - Return structured results
4. **View Results**: See license type, URL, confidence, and browser session details
5. **Download**: Export results as JSON for later use

## What It Finds

The browser automation searches for:

- **License Type**: CC-BY-4.0, MIT, Open Government License, etc.
- **License URL**: Direct link to the license page
- **Attribution Requirements**: How to credit the data
- **Usage Restrictions**: Any limitations on use
- **Confidence Level**: How certain the extraction is (high/medium/low)

## How It Works

1. **Initial Visit**: Browser visits the provided URL
2. **Link Discovery**: Identifies license-related links (e.g., "license", "terms", "legal")
3. **Multi-Page Search**: Navigates through up to multiple nested pages
4. **Content Analysis**: Uses LLM to validate and extract license information
5. **Synthesis**: Combines findings and returns structured data

## Browser Automation Sessions

The app shows:
- Number of browser sessions launched
- Type of each session
- Output from each browser
- Internal reasoning and decision-making process

## Example URLs to Try

- Government datasets: `https://data.gov/dataset/...`
- GitHub repositories: `https://github.com/user/repo`
- Research data portals: `https://dataverse.org/...`
- Statistics bureaus: `https://www.ssb.no/...`

## Command Line Alternative

For CLI usage, use the browser automation extractor:

```bash
python browser_automation_extractor.py <url> --mode=license
```

## API Models

- **moonshotai/kimi-k2-instruct-0905**: Fast, good for straightforward pages
- **groq/compound-mini**: Balance of speed and thoroughness
- **groq/compound**: Most comprehensive, may take longer

## Troubleshooting

- **No API Key**: Make sure GROQ_API_KEY is set in `.env` or entered in sidebar
- **Slow Results**: Compound models take longer but provide better results
- **No License Found**: Some pages may not have license information
- **Browser Sessions Failed**: Check your internet connection and API key

## Output Format

Results include:

```json
{
  "success": true,
  "content": "Full license details...",
  "license_data": {
    "license_type": "CC-BY-4.0",
    "license_url": "https://...",
    "confidence": "high"
  },
  "executed_tools": [...],
  "reasoning": "..."
}
```

## Notes

- Browser automation can launch up to 10 browsers simultaneously
- Results are more accurate than simple web scraping
- The app follows robots.txt and respects rate limits
- All processing happens through Groq's API

---

**Built with:** Groq Browser Automation API, Streamlit, Python
