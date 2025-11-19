# Comprehensive Metadata Extractor - Browser Automation

A Streamlit web application that uses Groq's browser automation API to extract comprehensive metadata from web pages, including license information, place types, place IDs, and date ranges by searching through nested links.

## Features

- 🤖 **Browser Automation**: Launches multiple browsers simultaneously to search through pages
- 🔍 **Deep Search**: Follows nested links across documentation, about pages, and data dictionaries
- 📄 **License Extraction**: License type, URL, attribution requirements, usage restrictions
- 🌍 **Place Coverage**: Geographic areas, place types, place ID systems, spatial resolution
- 📅 **Temporal Coverage**: Date ranges, update frequency, temporal resolution, data type
- 📊 **Structured Output**: All metadata organized in clear, tabbed interface
- 💾 **Export Results**: Download complete findings as JSON
- 📚 **URL History**: Quick access to recently analyzed URLs
- 🧠 **Transparent Process**: View browser automation reasoning and session details

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

1. **Enter a URL**: Paste the dataset or webpage URL you want to analyze
2. **Select Model** (optional): Choose between:
   - `moonshotai/kimi-k2-instruct-0905` (default, fast)
   - `groq/compound-mini` (more thorough)
   - `groq/compound` (most comprehensive)
3. **Click "Extract All Metadata"**: The app will:
   - Launch multiple browser automation sessions
   - Search the main page and nested links
   - Extract all metadata types
   - Return comprehensive structured results
4. **View Results**: Explore 5 tabs:
   - **Summary**: Overview of all extracted metadata
   - **License**: Complete license information
   - **Place/Geographic**: Geographic coverage and place types
   - **Date Range/Temporal**: Time coverage and update info
   - **Browser Sessions**: Automation process details
5. **Download**: Export complete results as JSON for later use

## What It Finds

The browser automation searches for comprehensive metadata:

### 📄 License Information
- **License Type**: CC-BY-4.0, MIT, Open Government License, etc.
- **License URL**: Direct link to the license page
- **Attribution Requirements**: How to credit the data
- **Usage Restrictions**: Any limitations on use
- **Confidence Level**: How certain the extraction is (high/medium/low)

### 🌍 Place/Geographic Coverage
- **Geographic Coverage**: Countries, regions, cities covered by the dataset
- **Place Types**: Country, State, City, PostalCode, etc.
- **Place ID Systems**: ISO 3166, FIPS codes, geonames IDs, etc.
- **Spatial Resolution**: Country-level, city-level, street-level, etc.
- **Example Place IDs**: Sample identifiers used in the data

### 📅 Temporal/Date Range Coverage
- **Coverage Period**: Start date and end date of the data
- **Update Frequency**: How often the data is updated (daily, monthly, annually)
- **Last Updated**: When the data was last refreshed
- **Temporal Resolution**: Daily, monthly, yearly data points
- **Reference Period**: Census date, survey period, etc.
- **Data Type**: Historical, real-time, or forecast data

## How It Works

1. **Initial Visit**: Browser visits the provided URL
2. **Link Discovery**: Identifies metadata-related links (license, documentation, about, data dictionary)
3. **Multi-Page Search**: Navigates through multiple nested pages simultaneously
4. **Content Analysis**: Uses LLM to validate and extract all metadata types
5. **Structured Parsing**: Organizes findings into license, place, and temporal categories
6. **Synthesis**: Combines all findings and returns comprehensive structured data

## Browser Automation Sessions

The app transparently shows:
- Number of browser sessions launched (can be up to 10 simultaneously)
- Type of each session (web_search, browser_automation)
- Output from each browser session
- Internal reasoning and decision-making process
- How the automation navigated through pages to find information

## Example URLs to Try

- Government datasets: `https://data.gov/dataset/...`
- GitHub repositories: `https://github.com/user/repo`
- Research data portals: `https://dataverse.org/...`
- Statistics bureaus: `https://www.ssb.no/...`

## Command Line Alternative

For CLI usage, use the browser automation extractor:

```bash
# Extract all metadata
python browser_automation_extractor.py <url> --mode=all

# Extract only license information
python browser_automation_extractor.py <url> --mode=license

# Extract only place information
python browser_automation_extractor.py <url> --mode=place

# Extract only temporal information
python browser_automation_extractor.py <url> --mode=temporal
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
  "content": "Full metadata details...",
  "parsed_metadata": {
    "license": {
      "license_type": "CC-BY-4.0",
      "license_url": "https://...",
      "attribution": "...",
      "restrictions": "...",
      "confidence": "high"
    },
    "place": {
      "geographic_coverage": {...},
      "place_types": ["Country", "State", "City"],
      "place_id_systems": {...},
      "spatial_resolution": "city-level"
    },
    "temporal": {
      "coverage_period": {
        "start_date": "2020-01-01",
        "end_date": "2024-12-31"
      },
      "update_frequency": {...},
      "temporal_resolution": "monthly",
      "data_type": "historical"
    }
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
