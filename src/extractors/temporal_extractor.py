"""Temporal extractor with multi-page crawling."""
import json
import re
from ..utils.groq_browser_client import GroqBrowserClient


class TemporalExtractor:
    """Extract temporal information from multiple pages."""

    def __init__(self, api_key: str):
        self.client = GroqBrowserClient(api_key)

    def extract(self, url: str) -> dict:
        """Extract temporal info by crawling multiple pages."""
        
        # Crawl up to 3 pages from the site
        pages = self.client.crawl_site(url, max_pages=3)
        
        if not pages:
            return {}
        
        # Combine content from all pages
        combined_content = "\n\n".join([content for _, content in pages])[:50000]
        
        prompt = """You are an expert data temporal analyst. Extract PRECISE temporal coverage information with HIGH ACCURACY (>90%).

TASK: Identify date ranges, update frequencies, and temporal resolution of the dataset.

INSTRUCTIONS:
1. COVERAGE PERIOD: Find the actual date range this dataset covers
   - Look for: "data from XXXX to YYYY", "time period: ...", "historical data since..."
   - Extract SPECIFIC dates/years (e.g., "1990", "2020-01-01", "1995 to present")
   - If ongoing, use "present" or "ongoing" for end_date
2. UPDATE FREQUENCY: How often is the data updated?
   - Look for: "updated annually", "monthly releases", "real-time", "quarterly updates"
   - Be specific: annual, monthly, quarterly, weekly, daily, hourly, real-time, on-demand
3. TEMPORAL RESOLUTION: What is the time granularity of individual data points?
   - yearly, monthly, weekly, daily, hourly, minute-level
4. LAST UPDATED: When was the dataset last updated?
   - Extract actual dates if mentioned

VALIDATION RULES:
- Only extract information explicitly stated in the content
- For date ranges, provide ACTUAL dates/years found, not estimates
- Be precise about frequency (e.g., "quarterly" not "regularly")
- If uncertain, set to null rather than guessing

Return ONLY valid JSON:
{
    "coverage_period": {
        "start_date": "earliest year/date mentioned (e.g., 1990, 2020-01-01, 1995-Q1)",
        "end_date": "latest year/date or 'present' or 'ongoing' or specific year"
    },
    "update_frequency": {
        "frequency": "how often updated: annual, monthly, quarterly, weekly, daily, real-time, etc."
    },
    "last_updated": "when dataset was last updated (YYYY-MM-DD or YYYY or null)",
    "temporal_resolution": "granularity of data: yearly, monthly, weekly, daily, hourly, minute-level"
}
Use null only if truly not found."""

        response = self.client.analyze(combined_content, prompt)

        try:
            response = response.strip()
            if response.startswith('```'):
                response = re.sub(r'^```json?\s*\n?', '', response)
                response = re.sub(r'\n?```\s*$', '', response)

            return json.loads(response)
        except:
            return {}
