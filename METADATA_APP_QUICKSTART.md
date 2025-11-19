# Quick Start Guide - Metadata Extractor App

## Run the App

```bash
# Option 1: Using streamlit command (if in PATH)
streamlit run license_finder_app.py

# Option 2: Using Python module
python3 -m streamlit run license_finder_app.py

# Option 3: Specify custom port
python3 -m streamlit run license_finder_app.py --server.port=8501
```

The app will open automatically in your browser at `http://localhost:8501`

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API key in `.env`:**
   ```bash
   echo "GROQ_API_KEY=your_key_here" > .env
   ```

3. **Run the app:**
   ```bash
   python3 -m streamlit run license_finder_app.py
   ```

## What the App Extracts

### 📄 License Information
- License type (e.g., CC-BY-4.0, MIT)
- License URL
- Attribution requirements
- Usage restrictions
- Confidence level

### 🌍 Place/Geographic Coverage
- Countries, regions, cities covered
- Place types (Country, State, City, etc.)
- Place ID systems (ISO 3166, FIPS, geonames)
- Spatial resolution
- Example place IDs

### 📅 Date Range/Temporal Coverage
- Coverage period (start/end dates)
- Update frequency
- Last updated date
- Temporal resolution (daily/monthly/yearly)
- Reference period
- Data type (historical/real-time/forecast)

## Using the App

1. **Enter URL** - Paste the dataset or webpage URL
2. **Select Model** (optional):
   - `moonshotai/kimi-k2-instruct-0905` - Fast (default)
   - `groq/compound-mini` - More thorough
   - `groq/compound` - Most comprehensive
3. **Click "Extract All Metadata"**
4. **View Results** in 5 tabs:
   - Summary
   - License
   - Place/Geographic
   - Date Range/Temporal
   - Browser Sessions
5. **Download** results as JSON

## Example URLs to Test

```bash
# Statistics Canada
https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000101

# Norway Statistics Bureau
https://www.ssb.no/en/statbank/table/06913

# Spain Open Data
https://datos.gob.es/en/catalogo/ea0010587-population-by-nationality

# GitHub Repository
https://github.com/matthiasn/lotti
```

## Tips

- **Faster Results**: Use default model `moonshotai/kimi-k2-instruct-0905`
- **Better Quality**: Use `groq/compound` for complex pages
- **View Process**: Check "Browser Sessions" tab to see how automation worked
- **Save Results**: Use download button to save JSON for later analysis
- **Recent URLs**: Click URLs in sidebar history to re-run extraction

## Troubleshooting

**App won't start:**
```bash
# Check if streamlit is installed
python3 -c "import streamlit; print(streamlit.__version__)"

# Reinstall if needed
pip install streamlit
```

**No API key:**
- Create `.env` file with `GROQ_API_KEY=your_key`
- Or enter key directly in app sidebar

**Port already in use:**
```bash
# Use different port
python3 -m streamlit run license_finder_app.py --server.port=8502
```

**Slow extraction:**
- Normal for comprehensive extraction (may take 30-60 seconds)
- Try faster model: `moonshotai/kimi-k2-instruct-0905`
- Check internet connection

## Command Line Alternative

For batch processing or scripting:

```bash
# Extract all metadata
python browser_automation_extractor.py https://example.com --mode=all

# Extract specific metadata type
python browser_automation_extractor.py https://example.com --mode=license
python browser_automation_extractor.py https://example.com --mode=place
python browser_automation_extractor.py https://example.com --mode=temporal

# Use different model
python browser_automation_extractor.py https://example.com --model=groq/compound

# Save to specific file
python browser_automation_extractor.py https://example.com --output=results.json
```

## Browser Automation Features

- **Parallel Browsing**: Launches up to 10 browsers simultaneously
- **Intelligent Navigation**: Follows relevant links (license, documentation, about pages)
- **Deep Search**: Searches through nested pages and data dictionaries
- **LLM Validation**: Uses AI to validate and extract accurate metadata
- **Transparent Process**: Shows all browser sessions and reasoning

## Output Files

App saves results with timestamp:
```
metadata_extraction_<url>_<timestamp>.json
```

Structure:
```json
{
  "url": "...",
  "extraction_type": "comprehensive_metadata",
  "timestamp": "2024-...",
  "result": {
    "parsed_metadata": {
      "license": {...},
      "place": {...},
      "temporal": {...}
    }
  }
}
```

---

**Need Help?** See [LICENSE_FINDER_README.md](LICENSE_FINDER_README.md) for full documentation.
