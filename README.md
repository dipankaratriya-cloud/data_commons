# Metadata Extractor Agent

An AI-powered web application that automatically extracts comprehensive metadata from data sources using Groq's browser automation capabilities. It identifies license information, geographic coverage, temporal coverage, and links to relevant data pages by intelligently navigating through websites.

## Features

- **Intelligent URL Detection** - Automatically finds official data source URLs from source names
- **Multi-Page Navigation** - Browser automation explores linked pages for comprehensive extraction
- **Structured Metadata Extraction** - License, geographic, and temporal coverage
- **Data Commons Integration** - Statistical variable search and entity property lookup
- **Country DCID Mapping** - Automatic linking of countries to Data Commons identifiers
- **Retry Mechanism** - Exponential backoff for transient failures
- **Progress Tracking** - Visual progress bar and status updates
- **Export Capability** - Download results as structured JSON

## Prerequisites

- **Python 3.10+** (Python 3.11 or 3.12 recommended)
- **Groq API Key** - Required for browser automation and metadata extraction
- **Data Commons API Key** (Optional) - For entity property lookup features

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/dipankaratriya-cloud/data_commons.git
cd data_commons
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the following packages:
- `groq>=0.4.0` - Groq API client for browser automation
- `python-dotenv>=1.0.0` - Environment variable management
- `streamlit>=1.28.0` - Web application framework
- `requests>=2.31.0` - HTTP client for API calls
- `beautifulsoup4>=4.12.0` - HTML parsing
- `lxml>=4.9.0` - XML/HTML processing

## Configuration

### Setting Up API Keys

1. **Create a `.env` file** in the project root directory:

```bash
# Copy the example (if available) or create a new file
touch .env
```

2. **Add your API keys** to the `.env` file:

```env
# Required - Get your Groq API key from https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here

# Optional - Get your Data Commons API key from https://apikeys.datacommons.org
DC_API_KEY=your_data_commons_api_key_here
```

### Getting API Keys

#### Groq API Key (Required)
1. Visit [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the key and add it to your `.env` file

#### Data Commons API Key (Optional)
1. Visit [https://apikeys.datacommons.org](https://apikeys.datacommons.org)
2. Request an API key
3. Once approved, add it to your `.env` file

## Running the Application

### Local Development

```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Run the Streamlit application
streamlit run license_finder_app.py
```

The application will start and open in your default web browser at `http://localhost:8501`.

### Custom Port

```bash
streamlit run license_finder_app.py --server.port 8080
```

### Running in Headless Mode (Server)

```bash
streamlit run license_finder_app.py --server.headless true
```

## Docker Deployment

### Build the Docker Image

```bash
docker build -t metadata-extractor .
```

### Run with Docker

```bash
# Run with environment variables
docker run -p 8080:8080 \
  -e GROQ_API_KEY=your_groq_api_key \
  -e DC_API_KEY=your_dc_api_key \
  metadata-extractor
```

### Using Docker Compose (Optional)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  metadata-extractor:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - DC_API_KEY=${DC_API_KEY}
```

Run with:
```bash
docker-compose up
```

## Usage Guide

### Tab 1: Metadata Extractor

1. **Enter a Source Name or URL**
   - Source name: e.g., "Statistics Canada", "French Open Data Portal"
   - Direct URL: e.g., "https://data.gov.uk"

2. **Add a Description** (required for source names)
   - Describe what information you're looking for
   - Example: "Find license type, geographic coverage, and date range for this education dataset"

3. **Click "Extract Metadata"**
   - The app will search for the URL (if source name given)
   - Browser automation will navigate the website
   - Metadata will be extracted and displayed

4. **View Results**
   - **Summary**: Complete extracted information
   - **License**: License type, URL, attribution requirements
   - **Place/Geographic**: Countries, regions, place types
   - **Date Range/Temporal**: Coverage period, update frequency
   - **Browser Sessions**: Details of automation sessions

5. **Download Results**
   - Click "Download Results as JSON" to save the extraction

### Tab 2: Entity Properties

1. **Search Statistical Variables**
   - Enter a search term (e.g., "agriculture", "population", "income")
   - Click "Search Statistical Variables"

2. **View Results**
   - See matching statistical variables from Data Commons
   - View constraint properties for each variable
   - Click links to view in Data Commons browser

## Project Structure

```
data_commons/
├── license_finder_app.py      # Main Streamlit application
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── .env                       # Environment variables (create this)
├── README.md                  # This file
├── ARCHITECTURE.md            # Detailed architecture documentation
└── src/
    ├── __init__.py
    ├── orchestrator.py        # Extraction orchestrator with validation
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

## API Integrations

### Groq API
- **Model**: `groq/compound`
- **Features Used**: Browser automation, web search
- **Documentation**: [https://groq.com/docs](https://groq.com/docs)

### Data Commons API
- **Endpoints Used**:
  - `/v2/sparql` - SPARQL queries for entity search
  - `/v2/node` - Fetch entity properties
  - `/v2/resolve` - Resolve entity names to DCIDs
  - `/v2/find` - Search for entities by query
- **Documentation**: [https://docs.datacommons.org/api](https://docs.datacommons.org/api)

## Troubleshooting

### Common Issues

#### "No API key found in .env file"
- Ensure you have created a `.env` file in the project root
- Verify `GROQ_API_KEY` is set correctly
- Check there are no extra spaces or quotes around the key

#### Rate Limit Errors (429)
- Wait for the specified time before retrying
- Consider upgrading your Groq plan for higher limits
- Try simpler URLs that require less processing

#### Request Too Large (413)
- Use the main website URL instead of specific data tables
- Try a simpler page with less content

#### Timeout Errors
- Increase the timeout in the sidebar (if available)
- Try the homepage instead of deep-linked pages
- Verify the website is accessible

#### Empty or No Results
- Try a more specific source name
- Enter the URL directly instead of a source name
- Check if the website is publicly accessible

### Debug Mode

To see detailed logs, run Streamlit with debug logging:

```bash
streamlit run license_finder_app.py --logger.level debug
```

## Default Settings

| Setting | Value |
|---------|-------|
| Model | `groq/compound` |
| Timeout | 240 seconds (4 minutes) |
| Max Retries | 3 |
| Temperature | 0.1 |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source. See the repository for license details.

## Support

For issues and feature requests, please open an issue on GitHub:
[https://github.com/dipankaratriya-cloud/data_commons/issues](https://github.com/dipankaratriya-cloud/data_commons/issues)

---

Built with Streamlit and powered by Groq Browser Automation
