# Metadata Extractor Agent - Architecture Documentation

> **Repository:** [https://github.com/dipankaratriya-cloud/data_commons](https://github.com/dipankaratriya-cloud/data_commons)

## Overview

The Metadata Extractor Agent is an AI-powered web application that automatically extracts comprehensive metadata from data sources using Groq's browser automation capabilities. It identifies license information, geographic coverage, temporal coverage, and links to relevant data pages by intelligently navigating through websites.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE (Streamlit)                        │
│                         license_finder_app.py                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┐     ┌─────────────────────────────────────┐   │
│  │   Metadata Extractor    │     │     Entity Properties Tool          │   │
│  │   (Tab 1)               │     │     (Tab 2)                         │   │
│  │   - URL/Source Input    │     │     - Statistical Variable Search   │   │
│  │   - Progress Tracking   │     │     - DC API Integration            │   │
│  │   - Results Display     │     │     - Property Viewer               │   │
│  └───────────┬─────────────┘     └─────────────┬───────────────────────┘   │
└──────────────┼─────────────────────────────────┼───────────────────────────┘
               │                                 │
               ▼                                 ▼
┌──────────────────────────────────┐  ┌──────────────────────────────────────┐
│    GROQ BROWSER AUTOMATION       │  │     DATA COMMONS API                 │
│    src/utils/groq_browser_       │  │     - v2/sparql                      │
│    automation.py                 │  │     - v2/node                        │
│                                  │  │     - v2/resolve                     │
│  ┌────────────────────────────┐  │  │     - v2/find                        │
│  │  extract_with_automation() │  │  └──────────────────────────────────────┘
│  │  ├─ Browser Automation     │  │
│  │  └─ Web Search             │  │
│  ├────────────────────────────┤  │
│  │  find_source_url()         │  │
│  │  extract_all_metadata()    │  │
│  │  extract_license_metadata()│  │
│  │  extract_place_metadata()  │  │
│  │  extract_temporal_metadata()│ │
│  └────────────────────────────┘  │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│        GROQ API (LLM)            │
│        Model: groq/compound      │
│                                  │
│  Features:                       │
│  - Browser automation tool       │
│  - Web search tool               │
│  - Multi-page navigation         │
└──────────────────────────────────┘
```

## Core Components

### 1. Main Application (`license_finder_app.py`)

The Streamlit-based frontend that provides the user interface and orchestrates metadata extraction.

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `main()` | Entry point, configures Streamlit UI and handles user interactions |
| `search_statistical_variables()` | Searches Data Commons for statistical variables with constraint properties |
| `find_dc_property()` | Finds Data Commons property for concepts (e.g., 'agriculture' -> 'economicSector') |
| `get_entity_properties()` | Fetches DC properties for entities by name (places, variables, topics) |
| `get_country_dcids()` | Extracts Data Commons DCIDs for countries mentioned in text |
| `format_comprehensive_display()` | Renders extraction results in organized tabs |
| `save_results_json()` | Exports results to downloadable JSON |

**Data Flow:**

```
User Input (URL/Source Name)
        │
        ▼
┌───────────────────────┐
│ URL Detection         │
│ (if source name given)│
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ GroqBrowserAutomation │
│ .extract_all_metadata │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Result Parsing &      │
│ Country DCID Injection│
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Tabbed Display:       │
│ - Summary             │
│ - License             │
│ - Place/Geographic    │
│ - Date Range/Temporal │
│ - Browser Sessions    │
└───────────────────────┘
```

### 2. Groq Browser Automation Client (`src/utils/groq_browser_automation.py`)

The core engine that interfaces with Groq's compound model to perform intelligent web browsing.

**Class: `GroqBrowserAutomation`**

```python
class GroqBrowserAutomation:
    def __init__(self, api_key: str, model: str = "groq/compound", timeout: int = 120)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `extract_with_automation()` | Core method that sends queries to Groq with browser_automation and web_search tools enabled |
| `find_source_url()` | Searches the web to find official URLs for a data source name |
| `extract_all_metadata()` | Comprehensive extraction of license, place, and temporal metadata |
| `extract_license_metadata()` | Focused extraction of license information |
| `extract_place_metadata()` | Focused extraction of geographic coverage |
| `extract_temporal_metadata()` | Focused extraction of temporal coverage |
| `_parse_license_content()` | Parses license info from LLM response |
| `_parse_place_content()` | Parses place info from LLM response |
| `_parse_temporal_content()` | Parses temporal info from LLM response |

**Retry Logic:**

```
┌─────────────────────────────────────────────┐
│           extract_with_automation()          │
├─────────────────────────────────────────────┤
│  for attempt in range(max_retries + 1):     │
│      try:                                    │
│          → Call Groq API                     │
│          → Return success result             │
│      except:                                 │
│          → Check if retryable error          │
│          → Exponential backoff (2s, 4s, 6s)  │
│          → Continue or break                 │
│  return failure result                       │
└─────────────────────────────────────────────┘
```

### 3. Orchestrator (`src/orchestrator.py`)

Alternative extraction pipeline with validation scoring.

**Class: `MetadataOrchestrator`**

```python
class MetadataOrchestrator:
    def __init__(self, api_key: str):
        self.license_extractor = LicenseExtractor(api_key)
        self.place_extractor = PlaceExtractor(api_key)
        self.temporal_extractor = TemporalExtractor(api_key)
```

**Validation Scoring System:**

| Extractor | Scoring Criteria | Max Score |
|-----------|------------------|-----------|
| License | license_type (40), license_url (30), attribution (15), high confidence (15) | 100 |
| Place | countries (25), regions (15), place_types (20), ID systems (20), examples (15), resolution (5) | 100 |
| Temporal | start_date (35), end_date (35), frequency (20), resolution (10) | 100 |

### 4. Specialized Extractors (`src/extractors/`)

Individual extraction modules for each metadata type:

- **`license_extractor.py`** - Multi-page crawling for license information
- **`place_extractor.py`** - Geographic coverage extraction
- **`temporal_extractor.py`** - Temporal coverage extraction

## Data Structures

### Extraction Result

```python
{
    "success": bool,
    "content": str,              # Raw LLM response
    "reasoning": str,            # LLM reasoning process
    "executed_tools": list,      # Browser sessions details
    "parsed_metadata": {
        "license": {
            "license_type": str,
            "license_url": str,
            "attribution": str,
            "restrictions": str,
            "confidence": str    # "high", "medium", "low"
        },
        "place": {
            "geographic_coverage": dict,
            "place_types": list,
            "place_id_systems": dict,
            "spatial_resolution": str
        },
        "temporal": {
            "coverage_period": {
                "start_date": str,
                "end_date": str
            },
            "update_frequency": dict,
            "temporal_resolution": str,
            "data_type": str
        }
    },
    "error": str                 # Error message if failed
}
```

### Country DCID Mapping

Built-in mapping of 50+ countries to Data Commons DCIDs:

```python
COUNTRY_DCIDS = {
    "united states": "country/USA",
    "france": "country/FRA",
    "norway": "country/NOR",
    # ... 50+ more mappings
}
```

## External Integrations

### 1. Groq API

```python
client = Groq(
    api_key=api_key,
    timeout=timeout,
    default_headers={"Groq-Model-Version": "latest"}
)

chat_completion = client.chat.completions.create(
    messages=[{"role": "user", "content": query}],
    model="groq/compound",
    temperature=0.1,
    compound_custom={
        "tools": {
            "enabled_tools": ["browser_automation", "web_search"]
        }
    }
)
```

### 2. Data Commons API

| Endpoint | Purpose |
|----------|---------|
| `/v2/sparql` | SPARQL queries for entity search |
| `/v2/node` | Fetch entity properties |
| `/v2/resolve` | Resolve entity names to DCIDs |
| `/v2/find` | Search for entities by query |

## Error Handling

The application handles multiple error scenarios:

| Error Type | Detection | Response |
|------------|-----------|----------|
| Rate Limit (429) | `"429"` or `"rate_limit_exceeded"` in error | Show wait time, auto-retry button |
| Request Too Large (413) | `"413"` or `"too large"` in error | Suggest simpler URLs |
| Timeout | `"timeout"` in error | Retry guidance |
| Connection Error | `"connection"` in error | Network check prompt |
| Auth Error | `"api key"` in error | API key configuration help |

## UI Components

### Tab Structure

```
┌──────────────────────────────────────────────────────────────┐
│  [Metadata Extractor]  [Entity Properties]                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Results Tabs (when extraction completes):                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [Summary] [License] [Place/Geographic] [Date Range] ... │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Sidebar

- API Configuration (auto-loaded from `.env`)
- Recent Sources History (last 5)
- Help/About Section

## Configuration

### Environment Variables

```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional (for Entity Properties tool)
DC_API_KEY=your_data_commons_api_key
```

### Default Settings

| Setting | Value |
|---------|-------|
| Model | `groq/compound` |
| Timeout | 240 seconds (4 minutes) |
| Max Retries | 3 |
| Temperature | 0.1 |

## File Structure

```
data_commons/
├── license_finder_app.py          # Main Streamlit application (1487 lines)
├── .env                           # Environment variables
├── ARCHITECTURE.md                # This documentation
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
└── src/
    ├── __init__.py
    ├── orchestrator.py            # Extraction orchestrator with validation
    ├── utils/
    │   ├── __init__.py
    │   ├── groq_browser_automation.py  # Core browser automation client
    │   ├── groq_browser_client.py      # Alternative browser client
    │   └── auth.py                     # Authentication utilities
    └── extractors/
        ├── __init__.py
        ├── license_extractor.py        # License extraction
        ├── place_extractor.py          # Place/geographic extraction
        └── temporal_extractor.py       # Temporal extraction
```

## Usage Flow

```
1. User enters source name (e.g., "Statistics Canada")
   OR direct URL (e.g., "https://statcan.gc.ca")
           │
           ▼
2. If source name → find_source_url() searches web for official URL
           │
           ▼
3. extract_all_metadata() sends comprehensive prompt to Groq
           │
           ▼
4. Groq compound model uses browser_automation + web_search
   to navigate pages and extract information
           │
           ▼
5. Response parsed → license, place, temporal data extracted
           │
           ▼
6. Country DCIDs injected from built-in mapping
           │
           ▼
7. Results displayed in tabbed interface
           │
           ▼
8. User can download results as JSON
```

## Key Features

1. **Intelligent URL Detection** - Automatically finds official data source URLs from source names
2. **Multi-Page Navigation** - Browser automation explores linked pages for comprehensive extraction
3. **Structured Metadata Extraction** - License, geographic, and temporal coverage
4. **Data Commons Integration** - Statistical variable search and entity property lookup
5. **Country DCID Mapping** - Automatic linking of countries to Data Commons identifiers
6. **Retry Mechanism** - Exponential backoff for transient failures
7. **Progress Tracking** - Visual progress bar and status updates
8. **Export Capability** - Download results as structured JSON

## Dependencies

```
streamlit
groq
requests
python-dotenv
```

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run the app
streamlit run license_finder_app.py
```

## License

See repository for license information.

---

*Documentation generated for the Metadata Extractor Agent*
