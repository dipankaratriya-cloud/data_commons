"""Place extractor with multi-page crawling."""
import json
import re
from ..utils.groq_browser_client import GroqBrowserClient


class PlaceExtractor:
    """Extract place information from multiple pages."""

    def __init__(self, api_key: str):
        self.client = GroqBrowserClient(api_key)

    def extract(self, url: str) -> dict:
        """Extract place info by crawling multiple pages."""
        
        # Crawl up to 3 pages from the site
        pages = self.client.crawl_site(url, max_pages=3)
        
        if not pages:
            return {}
        
        # Combine content from all pages
        combined_content = "\n\n".join([content for _, content in pages])[:50000]
        
        prompt = """You are an expert geographic data analyst. Extract PRECISE geographic and place information with HIGH ACCURACY (>90%).

TASK: Identify geographic coverage, place types, and ID resolution methods.

INSTRUCTIONS:
1. GEOGRAPHIC COVERAGE: List all countries, regions, states, provinces explicitly mentioned
2. PLACE TYPES: Identify the hierarchical levels (e.g., Country > Province > County > City > Municipality)
3. PLACE ID SYSTEMS: Find ID/code systems used to identify places
   - Look for: ISO codes (ISO-3166-1, ISO-3166-2), NUTS codes, FIPS codes, postal codes, GENC, statistical codes
   - Extract actual example IDs from the content (e.g., "CA" for Canada, "US-NY" for New York, "FR-75" for Paris)
4. ID RESOLUTION METHOD: Describe HOW to resolve/lookup these IDs (APIs, lookup tables, documentation links)

VALIDATION RULES:
- Only include information explicitly found in the content
- For ID systems, provide REAL examples from the page, not made-up ones
- Be specific about ID resolution (e.g., "ISO 3166-1 alpha-2 codes resolvable via iso.org")

Return ONLY valid JSON:
{
    "geographic_coverage": {
        "countries": ["list all countries explicitly mentioned"],
        "regions": ["list states/provinces/regions explicitly mentioned"]
    },
    "place_types": ["list hierarchical place types found: Country, Province, County, City, etc."],
    "place_id_systems": {
        "systems": ["list ID systems like ISO-3166-1, ISO-3166-2, NUTS, postal codes, FIPS"],
        "examples": ["provide 5-10 ACTUAL example IDs extracted from content"],
        "resolution_method": "describe how to resolve these IDs (API, lookup table, documentation URL)"
    }
}
Use null or [] only if truly not found."""

        response = self.client.analyze(combined_content, prompt)

        try:
            response = response.strip()
            if response.startswith('```'):
                response = re.sub(r'^```json?\s*\n?', '', response)
                response = re.sub(r'\n?```\s*$', '', response)

            return json.loads(response)
        except:
            return {}
