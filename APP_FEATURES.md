# Metadata Extractor App - Feature Overview

## App Architecture

```
User Input (URL)
       ↓
Groq Browser Automation API
       ↓
Multiple Browser Sessions (up to 10 parallel)
       ↓
Page Navigation & Content Extraction
       ↓
LLM Analysis & Validation
       ↓
Structured Metadata Output
       ↓
Display in 5 Tabs + JSON Export
```

## User Interface Components

### Main Input
- **URL Text Input**: Enter dataset or webpage URL
- **Model Selector**: Choose AI model (default, mini, or full compound)
- **Extract Button**: Trigger the metadata extraction

### Output Tabs

#### 1. 📋 Summary Tab
- Quick overview cards showing:
  - License type
  - Place coverage highlights (first 3 types)
  - Date range (start/end dates)
- Expandable full content section

#### 2. 📄 License Tab
Displays:
- License Type (e.g., CC-BY-4.0)
- License URL (clickable link)
- Confidence level (🟢 High / 🟡 Medium / 🔴 Low)
- Attribution requirements
- Usage restrictions

#### 3. 🌍 Place/Geographic Tab
Shows:
- **Geographic Coverage**: Countries, regions, cities
- **Place Types**: Country, State, City, PostalCode, etc. (displayed as cards)
- **Place ID Systems**: ISO 3166, FIPS codes, geonames, etc.
- **Spatial Resolution**: Level of geographic detail

#### 4. 📅 Date Range/Temporal Tab
Includes:
- **Coverage Period**: Start date ↔ End date (shown as metrics)
- **Update Information**: Frequency, last updated
- **Temporal Resolution**: Daily, monthly, yearly
- **Data Type**: Historical, real-time, or forecast

#### 5. 🔧 Browser Sessions Tab
Reveals:
- Number of browser sessions launched
- Expandable details for each session:
  - Session type
  - Output preview (first 500 chars)
- **Browser Automation Reasoning**:
  - Detailed process explanation
  - Decision-making steps
  - Navigation path

### Sidebar Features

#### Configuration
- **API Key Status**: Shows if key is loaded from environment
- **Manual API Key Input**: Enter key if not in .env
- **Model Selection**: Dropdown with 3 model options

#### URL History
- Shows last 5 analyzed URLs
- Click to quickly re-run extraction
- Truncated display (first 35 characters)

#### Help Section
- Expandable "How it works" guide
- Lists all extracted metadata types
- Explains browser automation process

### Download
- **JSON Export Button**: Downloads complete results
- Filename format: `metadata_extraction_<url>_<timestamp>.json`
- Includes all extracted metadata + browser session details

## Browser Automation Capabilities

### What the API Does
1. **Launches Browsers**: Up to 10 simultaneous browser instances
2. **Intelligent Navigation**: Finds and follows relevant links:
   - "license", "terms", "legal"
   - "documentation", "about", "metadata"
   - "data dictionary", "coverage", "temporal"
3. **Content Extraction**: Scrapes and analyzes page content
4. **LLM Validation**: Uses AI to validate and structure findings
5. **Multi-Page Synthesis**: Combines information from multiple sources

### Browser Session Types
- **web_search**: Search engine queries for finding pages
- **browser_automation**: Actual page visits and content extraction

### Search Strategy
The automation:
- Starts at the main URL
- Identifies relevant navigation paths
- Follows links to documentation/metadata pages
- Extracts content from each page
- Validates findings with LLM
- Synthesizes comprehensive results

## Data Flow

### Input Processing
```
URL → Validation → API Call
```

### Browser Automation
```
Main Page Visit
    ↓
Link Discovery → [License Links, Documentation, About Pages]
    ↓
Parallel Navigation → [Page 1, Page 2, ..., Page N]
    ↓
Content Extraction → [Text, Metadata, Links]
    ↓
LLM Analysis → [Validate, Structure, Parse]
    ↓
Combine Results
```

### Output Generation
```
Raw Results
    ↓
Parse into Categories → [License, Place, Temporal]
    ↓
Format for Display → [Tabs, Cards, Metrics]
    ↓
Generate JSON → [Downloadable File]
```

## API Models Comparison

| Model | Speed | Thoroughness | Best For |
|-------|-------|--------------|----------|
| **moonshotai/kimi-k2-instruct-0905** | ⚡⚡⚡ Fast | ⭐⭐ Good | Simple pages, quick results |
| **groq/compound-mini** | ⚡⚡ Medium | ⭐⭐⭐ Better | Moderate complexity |
| **groq/compound** | ⚡ Slower | ⭐⭐⭐⭐ Best | Complex sites, max accuracy |

## Extracted Metadata Structure

### License Object
```python
{
    "license_type": str,        # e.g., "CC-BY-4.0"
    "license_url": str,         # Direct link
    "attribution": str,         # Requirements
    "restrictions": str,        # Limitations
    "confidence": str           # "high", "medium", "low"
}
```

### Place Object
```python
{
    "geographic_coverage": dict,      # Countries, regions, cities
    "place_types": list,              # ["Country", "State", ...]
    "place_id_systems": dict,         # ISO codes, FIPS, etc.
    "spatial_resolution": str         # "city-level", etc.
}
```

### Temporal Object
```python
{
    "coverage_period": {
        "start_date": str,            # "2020-01-01"
        "end_date": str               # "2024-12-31"
    },
    "update_frequency": dict,         # How often updated
    "temporal_resolution": str,       # "daily", "monthly", etc.
    "data_type": str                  # "historical", "real-time"
}
```

## User Experience Features

### Loading States
- Spinner with descriptive message during extraction
- Real-time progress indication
- Clear success/error messages

### Error Handling
- API key validation
- URL validation
- Graceful error display
- Exception details shown for debugging

### Visual Feedback
- Color-coded confidence levels (🟢🟡🔴)
- Info/Success/Warning/Error message styling
- Metric cards for key values
- Expandable sections for detailed info

### Persistence
- Session state for URL history
- Selected URL carries over
- History survives page refreshes

## Performance Characteristics

### Typical Extraction Times
- **Simple page** (moonshotai): 10-20 seconds
- **Moderate page** (compound-mini): 20-40 seconds
- **Complex page** (compound): 30-60 seconds

### Browser Session Counts
- **Simple extraction**: 1-3 sessions
- **Moderate extraction**: 3-6 sessions
- **Comprehensive extraction**: 5-10 sessions

### Success Factors
- ✅ Clear metadata on page
- ✅ Good HTML structure
- ✅ Linked documentation pages
- ✅ Standard licensing info
- ❌ JavaScript-heavy dynamic content
- ❌ Gated/authenticated content
- ❌ Non-standard metadata formats

## Integration Points

### Environment Variables
- `GROQ_API_KEY`: Required for API access

### File Outputs
- JSON exports with timestamp
- Automatic filename generation
- Complete metadata + session details

### API Endpoints
- Groq Browser Automation API
- Model: configurable
- Headers: `Groq-Model-Version: latest`

## Future Enhancement Ideas

- [ ] Batch URL processing
- [ ] CSV/Excel export options
- [ ] Comparison view for multiple URLs
- [ ] Scheduling/automated extraction
- [ ] Webhook notifications
- [ ] Custom extraction prompts
- [ ] Metadata quality scoring
- [ ] Historical tracking of changes
- [ ] API rate limit handling
- [ ] Caching layer for repeated URLs

---

**Built with:** Streamlit, Groq Browser Automation API, Python 3.x
