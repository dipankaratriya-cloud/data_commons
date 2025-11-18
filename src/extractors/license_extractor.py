"""License extractor with multi-page crawling and LLM validation."""
import json
import re
from ..utils.groq_browser_client import GroqBrowserClient


class LicenseExtractor:
    """Extract and validate license information across multiple pages."""

    def __init__(self, api_key: str):
        self.client = GroqBrowserClient(api_key)

    def extract(self, url: str) -> dict:
        """Extract license info by crawling and validating with LLM."""
        
        # Find specific license links
        license_links = self.client.find_license_links(url)
        
        # Crawl license pages and main page
        pages_to_check = [url] + license_links[:3]
        all_findings = []
        
        for page_url in pages_to_check:
            content = self.client.scrape_page(page_url)
            if not content:
                continue
            
            # Ask LLM to extract license info
            prompt = f"""Analyze this webpage and extract license or terms of use information.

Look for:
- License names (e.g., "Open Government Licence", "CC-BY", "MIT License")
- Terms of use or terms and conditions pages
- Copyright information
- Data usage policies
- Any legal information about using the data

IMPORTANT: If you find ANY form of legal terms, licensing, or usage policy information, set has_license to true.

Return ONLY valid JSON:
{{
    "license_type": "license name if found, otherwise 'Terms of Use' or 'Usage Policy'",
    "license_url": "{page_url}",
    "has_license": true/false,
    "confidence": "high/medium/low"
}}

Page URL: {page_url}"""

            response = self.client.analyze(content, prompt)
            
            try:
                response = response.strip()
                if response.startswith('```'):
                    response = re.sub(r'^```json?\s*\n?', '', response)
                    response = re.sub(r'\n?```\s*$', '', response)
                
                data = json.loads(response)
                
                # Only include if LLM confirmed it has license info
                if data.get('has_license'):
                    all_findings.append(data)
            except:
                continue
        
        # Select best finding based on confidence and specificity
        if not all_findings:
            # Fallback: return main URL if no license found
            return {
                "success": True,
                "best_match": {
                    "license_url": url,
                    "license_type": None,
                    "confidence": "low"
                }
            }

        # Prefer high confidence findings with specific license types
        best = max(all_findings, key=lambda x: (
            x.get('confidence') == 'high',
            bool(x.get('license_type')) and x.get('license_type') not in ['null', None, ''],
            bool(x.get('license_url'))
        ))

        return {"success": True, "best_match": best}
