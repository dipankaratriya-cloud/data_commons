# Quick Start Guide

## Installation

1. Navigate to the project directory:
```bash
cd /Users/dipankar/Documents/Data_commons_main/groq_browser_extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Run the Application

Start the Streamlit web app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Using the Web Interface

1. **Enter API Key**: In the sidebar, paste your Groq API key
2. **Configure Options**:
   - Check/uncheck which metadata to extract (License, Place, Temporal)
   - Adjust "Max License Links to Follow" slider (recommended: 3)
3. **Enter URL**: Paste the dataset URL in the main input field
4. **Extract**: Click the "Extract Metadata" button
5. **View Results**: Browse through the tabs to see extracted metadata

## Example Usage

### Using the Python API

```python
from src.orchestrator import MetadataOrchestrator

# Initialize with your API key
orchestrator = MetadataOrchestrator(groq_api_key="your-groq-api-key")

# Extract all metadata
results = orchestrator.extract_metadata(
    url="https://www.ons.gov.uk/datasets/TS007/editions/2021/versions/1",
    extract_license=True,
    extract_place=True,
    extract_temporal=True
)

# Print license information
if results['license']:
    best = results['license']['best_match']
    print(f"License: {best['license_type']}")
    print(f"URL: {best['license_url']}")
    print(f"Confidence: {best['confidence']}")
```

### Extract Only License Information

```python
from src.extractors.license_extractor import LicenseExtractor

extractor = LicenseExtractor(groq_api_key="your-groq-api-key")
result = extractor.extract(
    url="https://example.com/dataset",
    max_follow_links=3
)

# Access results
print("Main page:", result['main_page'])
print("Followed links:", result['followed_links'])
print("Best match:", result['best_match'])
```

## Tips for Best Results

1. **License Extraction**:
   - Set `max_follow_links` to 3-5 for thorough searching
   - The system automatically scores and prioritizes license-specific URLs
   - Check the "Best Match" section for the most reliable result

2. **API Key**:
   - Get your free Groq API key at https://console.groq.com
   - Keep your API key secure and never commit it to version control

3. **Large Datasets**:
   - The hybrid approach (scraping + Groq) is cost-effective
   - Web scraping reduces API calls while maintaining accuracy

4. **Troubleshooting**:
   - If scraping fails, the system automatically falls back to Groq Browser API
   - Check the "Raw JSON" tab for detailed error messages
   - Verify the URL is publicly accessible

## Output Structure

### License Output (Markdown)
The web interface displays clickable links:
- Main Page Analysis
- Followed License Links (with scores)
- Best Match (recommended result)

### Place Output
- Geographic Coverage (countries, regions, cities)
- Place Types
- Place ID Systems
- Spatial Resolution
- Coordinate System

### Temporal Output
- Coverage Period (start/end dates)
- Update Frequency
- Last Updated
- Temporal Resolution
- Reference Period
- Data Type (historical/real-time)

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize URL scoring patterns in `src/extractors/license_extractor.py`
- Adjust prompts in extractor files for better results
- Integrate the extractors into your own pipelines

## Support

For issues or questions, check the troubleshooting section in README.md
