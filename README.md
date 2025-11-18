# Groq Browser Extractor

A hybrid metadata extraction system that combines web scraping with Groq's Browser API to extract license, place, and temporal metadata from dataset URLs.

## Features

### Hybrid License Extraction
- **Two-level web scraping**: Scrapes main page and follows license-related links
- **Intelligent link discovery**: Finds links with license-related keywords (license, licence, terms, copyright, etc.)
- **URL scoring by specificity**: Prioritizes links based on relevance to licensing
  - `open-licence` / `open-license` (score: 10)
  - `licence` / `license` (score: 8)
  - `licensing` (score: 7)
  - `copyright` (score: 5)
  - `legal` (score: 4)
  - `terms` (score: 3)
- **Smart fallback**: Uses Groq Browser API when scraping fails
- **Best match selection**: Automatically selects the most reliable license information

### Place Information Extraction
- Geographic coverage (countries, regions, cities)
- Place types (administrative areas, postal codes, etc.)
- Place ID systems (ISO codes, postal codes, statistical geography codes)
- Spatial resolution and coordinate systems

### Temporal Information Extraction
- Time period coverage (start/end dates)
- Update frequency
- Last update date
- Temporal resolution (daily, monthly, yearly)
- Reference periods and data type (historical/real-time)

## Installation

1. Clone the repository:
```bash
cd /Users/dipankar/Documents/Data_commons_main/groq_browser_extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- `groq` - Groq API client
- `streamlit` - Web application framework
- `requests` - HTTP library for web scraping
- `beautifulsoup4` - HTML parsing library
- `lxml` - XML/HTML parser (optional but recommended)

## Usage

### Streamlit Web Application

Run the interactive web application:

```bash
streamlit run app.py
```

Features:
- Enter your Groq API key in the sidebar
- Input dataset URL
- Select which metadata types to extract
- Configure max license links to follow
- View results with clickable markdown links
- Export raw JSON output

### Python API

```python
from src.orchestrator import MetadataOrchestrator

# Initialize orchestrator
orchestrator = MetadataOrchestrator(groq_api_key="your-api-key")

# Extract all metadata
results = orchestrator.extract_metadata(
    url="https://example.com/dataset",
    extract_license=True,
    extract_place=True,
    extract_temporal=True
)

# Extract specific metadata
license_info = orchestrator.extract_license("https://example.com/dataset")
place_info = orchestrator.extract_place("https://example.com/dataset")
temporal_info = orchestrator.extract_temporal("https://example.com/dataset")
```

### Individual Extractors

#### License Extractor

```python
from src.extractors.license_extractor import LicenseExtractor

extractor = LicenseExtractor(groq_api_key="your-api-key")

# Extract with default settings (follows up to 3 links)
result = extractor.extract(url="https://example.com/dataset")

# Custom link following
result = extractor.extract(url="https://example.com/dataset", max_follow_links=5)

# Result structure:
# {
#     'main_page': {...},          # License info from main page
#     'followed_links': [...],     # License info from followed links
#     'best_match': {...},         # Best license info selected
#     'all_sources': [...]         # All extracted license info
# }
```

#### Place Extractor

```python
from src.extractors.place_extractor import PlaceExtractor

extractor = PlaceExtractor(groq_api_key="your-api-key")
result = extractor.extract(url="https://example.com/dataset")

# Result includes:
# - geographic_coverage (countries, regions, cities)
# - place_types
# - place_id_systems
# - spatial_resolution
# - coordinate_system
```

#### Temporal Extractor

```python
from src.extractors.temporal_extractor import TemporalExtractor

extractor = TemporalExtractor(groq_api_key="your-api-key")
result = extractor.extract(url="https://example.com/dataset")

# Result includes:
# - coverage_period (start_date, end_date)
# - update_frequency
# - last_updated
# - temporal_resolution
# - reference_period
# - data_type
```

## Architecture

### Hybrid Approach

The system uses a hybrid approach combining:

1. **Web Scraping** (requests + BeautifulSoup):
   - Fast and cost-effective
   - Direct HTML parsing
   - Link discovery and following
   - Removes noise (scripts, styles, navigation)

2. **Groq Browser API**:
   - Intelligent content analysis
   - Structured data extraction
   - Handles dynamic content
   - Fallback when scraping fails

### License Extraction Workflow

```
1. Scrape main page
   ↓
2. Extract license info using Groq
   ↓
3. Find license-related links
   ↓
4. Score links by specificity
   ↓
5. Follow top-scored links
   ↓
6. Scrape each linked page
   ↓
7. Extract license info from each
   ↓
8. Select best match based on:
   - Confidence score
   - Link specificity
   - Completeness of information
```

### Project Structure

```
groq_browser_extractor/
├── app.py                          # Streamlit web application
├── README.md                       # This file
├── requirements.txt                # Python dependencies
└── src/
    ├── orchestrator.py            # Coordinates all extractors
    ├── utils/
    │   └── groq_browser_client.py # Groq API client wrapper
    └── extractors/
        ├── license_extractor.py   # License extraction (hybrid)
        ├── place_extractor.py     # Place information extraction
        └── temporal_extractor.py  # Temporal coverage extraction
```

## Configuration

### Environment Variables

You can set your Groq API key as an environment variable:

```bash
export GROQ_API_KEY="your-api-key-here"
```

### Customization

#### License Extractor

Customize URL scoring patterns in `license_extractor.py`:

```python
URL_PATTERNS = {
    'open-licence': 10,    # Highest priority
    'open-license': 10,
    'licence': 8,
    'license': 8,
    'licensing': 7,
    'copyright': 5,
    'legal': 4,
    'terms': 3,           # Lowest priority
}
```

#### Groq Client

Customize model and parameters in `groq_browser_client.py`:

```python
client = GroqBrowserClient(
    api_key="your-key",
    model="moonshotai/kimi-k2-instruct-0905"  # Default model
)

# Adjust temperature and tokens
result = client.browse_and_analyze(
    url="https://example.com",
    analysis_prompt="...",
    temperature=0.1,      # Lower = more focused
    max_tokens=2000       # Adjust as needed
)
```

## Output Format

### License Information

```json
{
    "main_page": {
        "license_type": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "attribution": "Credit must be given to the creator",
        "restrictions": "None",
        "confidence": "high",
        "source_url": "https://example.com/dataset"
    },
    "followed_links": [...],
    "best_match": {...},
    "all_sources": [...]
}
```

### Place Information

```json
{
    "geographic_coverage": {
        "countries": ["United Kingdom", "England"],
        "regions": ["Greater London"],
        "cities": ["London"],
        "description": "Data covers all of England"
    },
    "place_types": ["Administrative areas", "Statistical geographies"],
    "place_id_systems": {
        "systems": ["ONS geography codes", "ISO 3166-2"],
        "examples": ["E92000001"],
        "description": "Uses ONS standard geography codes"
    },
    "spatial_resolution": "Local authority level",
    "coordinate_system": "EPSG:4326 (WGS84)",
    "confidence": "high"
}
```

### Temporal Information

```json
{
    "coverage_period": {
        "start_date": "2011",
        "end_date": "2021",
        "description": "Census data from 2011 and 2021"
    },
    "update_frequency": {
        "frequency": "every 10 years",
        "description": "Updated with each census"
    },
    "last_updated": "2022-06-28",
    "temporal_resolution": "Point-in-time (census day)",
    "reference_period": "Census day 2021",
    "data_type": "historical",
    "confidence": "high"
}
```

## Best Practices

1. **API Key Security**: Never commit API keys to version control
2. **Rate Limiting**: Be mindful of API rate limits when processing many URLs
3. **Link Following**: Adjust `max_follow_links` based on your needs (3-5 recommended)
4. **Error Handling**: Check the `errors` field in results for any issues
5. **Confidence Scores**: Use confidence scores to filter results
6. **Caching**: Consider caching results to avoid redundant API calls

## Troubleshooting

### Scraping Issues

If web scraping fails:
- Check if the site allows scraping (robots.txt)
- Verify the URL is accessible
- The system will automatically fallback to Groq Browser API

### API Errors

If Groq API calls fail:
- Verify your API key is correct
- Check your API quota/rate limits
- Review error messages in the logs or UI

### No Results

If no metadata is extracted:
- Verify the URL contains relevant information
- Try adjusting the prompts in extractor files
- Check confidence scores in results

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues or questions:
- Check the troubleshooting section
- Review the code documentation
- Open an issue on GitHub
