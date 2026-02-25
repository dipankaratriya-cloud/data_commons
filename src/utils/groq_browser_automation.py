"""Groq Browser Automation Client for advanced web research."""
import json
from groq import Groq


class GroqBrowserAutomation:
    """Client for Groq's browser automation capabilities.

    Enables launching and controlling multiple browsers simultaneously
    for comprehensive web research and metadata extraction.
    """

    def __init__(self, api_key: str, model: str = "groq/compound", timeout: int = 120):
        """Initialize the browser automation client.

        Args:
            api_key: Groq API key
            model: Model to use (default: groq/compound)
            timeout: Request timeout in seconds (default: 120)
        """
        self.client = Groq(
            api_key=api_key,
            timeout=timeout,
            default_headers={
                "Groq-Model-Version": "latest"
            }
        )
        self.model = model
        self.timeout = timeout

    def extract_with_automation(self, query: str, temperature: float = 0.1, max_retries: int = 2) -> dict:
        """Extract information using browser automation.

        Args:
            query: The question or extraction prompt
            temperature: Model temperature (0.0-1.0)
            max_retries: Maximum number of retry attempts (default: 2)

        Returns:
            dict containing:
                - content: Final synthesized response
                - reasoning: Internal decision-making process
                - executed_tools: Details of browser automation sessions
                - raw_response: Full response object
        """
        import time

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": query,
                        }
                    ],
                    model=self.model,
                    temperature=temperature,
                    compound_custom={
                        "tools": {
                            "enabled_tools": ["browser_automation", "web_search"]
                        }
                    }
                )

                message = chat_completion.choices[0].message

                return {
                    "success": True,
                    "content": message.content,
                    "reasoning": getattr(message, 'reasoning', None),
                    "executed_tools": getattr(message, 'executed_tools', []),
                    "raw_response": message
                }

            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Don't retry on certain errors
                if any(x in error_str for x in ["api key", "authentication", "unauthorized", "forbidden"]):
                    return {
                        "success": False,
                        "error": f"Authentication error: {str(e)}",
                        "content": None,
                        "reasoning": None,
                        "executed_tools": []
                    }

                # Retry on timeout or temporary errors
                if attempt < max_retries:
                    if any(x in error_str for x in ["timeout", "timed out", "connection", "temporary"]):
                        wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                        time.sleep(wait_time)
                        continue

                # If we've exhausted retries or it's a non-retryable error
                break

        # If all retries failed
        return {
            "success": False,
            "error": str(last_error),
            "content": None,
            "reasoning": None,
            "executed_tools": []
        }

    def extract_license_metadata(self, url: str, max_retries: int = 2) -> dict:
        """Extract license metadata using browser automation.

        Args:
            url: Dataset or website URL
            max_retries: Maximum retry attempts (default: 2)

        Returns:
            dict with license information
        """
        query = f"""Analyze this dataset URL and extract license information: {url}

Please provide:
1. License Type (e.g., CC-BY-4.0, MIT, Open Government License, etc.)
2. License URL (direct link to license page)
3. Attribution requirements (if any)
4. Usage restrictions (if any)
5. Confidence level (high/medium/low)

Search through multiple pages if needed to find accurate license information.
Return the information in a structured format."""

        result = self.extract_with_automation(query, max_retries=max_retries)

        if result["success"]:
            # Parse the content to structure it better
            result["license_data"] = self._parse_license_content(result["content"])

        return result

    def extract_place_metadata(self, url: str, max_retries: int = 2) -> dict:
        """Extract geographic/place metadata using browser automation.

        Args:
            url: Dataset or website URL
            max_retries: Maximum retry attempts (default: 2)

        Returns:
            dict with place/geographic information
        """
        query = f"""Analyze this dataset URL and extract geographic coverage information: {url}

Please provide:
1. Geographic Coverage (countries, regions, cities covered)
2. Place Types (e.g., Country, State, City, PostalCode)
3. Place ID Systems used (e.g., ISO 3166, FIPS, geonames)
4. Spatial Resolution (e.g., country-level, city-level, street-level)
5. Example place IDs if available

Search through multiple pages including documentation, metadata, and data dictionaries.
Return the information in a structured format."""

        result = self.extract_with_automation(query, max_retries=max_retries)

        if result["success"]:
            result["place_data"] = self._parse_place_content(result["content"])

        return result

    def extract_temporal_metadata(self, url: str, max_retries: int = 2) -> dict:
        """Extract temporal metadata using browser automation.

        Args:
            url: Dataset or website URL
            max_retries: Maximum retry attempts (default: 2)

        Returns:
            dict with temporal/time-based information
        """
        query = f"""Analyze this dataset URL and extract temporal coverage information: {url}

Please provide:
1. Coverage Period (start date and end date)
2. Update Frequency (e.g., daily, monthly, annually)
3. Last Updated date
4. Temporal Resolution (e.g., daily, monthly, yearly data points)
5. Reference Period (census date, survey period, etc.)
6. Data Type (historical, real-time, forecast)

Search through multiple pages including documentation and metadata sections.
Return the information in a structured format."""

        result = self.extract_with_automation(query, max_retries=max_retries)

        if result["success"]:
            result["temporal_data"] = self._parse_temporal_content(result["content"])

        return result

    def find_source_url(self, source_name: str, max_retries: int = 3) -> dict:
        """Find the official dataset/data portal URL for a given source name.

        Args:
            source_name: Name of the data source (e.g., "Statistics Canada", "French Open Data")
            max_retries: Maximum retry attempts (default: 3)

        Returns:
            dict with url and source details
        """
        import time
        import re

        source_name = source_name.strip()
        # Parse source name - replace underscores/camelCase with spaces for better search
        search_terms = re.sub(r'([a-z])([A-Z])', r'\1 \2', source_name)
        search_terms = search_terms.replace('_', ' ').replace('-', ' ')

        # Different query variations to try
        queries = [
            f"""Search the web for: {search_terms}

This is a dataset/data source name. Find the EXACT webpage that contains this data.

Return JSON with 3 URLs:
- url: main website of the data provider
- license_url: terms/conditions page on same website
- data_url: the SPECIFIC page URL where this exact data is published

{{"url": "https://...", "license_url": "https://...", "data_url": "https://..."}}""",

            f"""Find the official website for "{search_terms}" data portal or statistics agency.

Search and return the main URL for this data source. This is likely a government statistics agency or open data portal.

Return as JSON: {{"url": "https://...", "license_url": "https://...", "data_url": "https://..."}}""",

            f"""What is the official website URL for {search_terms}?

Search the web and find the homepage URL for this organization's data portal.

Return JSON format: {{"url": "https://..."}}"""
        ]

        last_result = None

        for attempt in range(max_retries):
            # Use different query variations
            query = queries[attempt % len(queries)]

            result = self.extract_with_automation(query, max_retries=1)
            last_result = result

            if result["success"] and result["content"]:
                content = result["content"]

                # Try to extract JSON from the response
                json_match = re.search(r'\{[^{}]*"url"[^{}]*\}', content, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group())
                        result["detected_url"] = parsed.get("url")
                        result["license_url"] = parsed.get("license_url")
                        result["data_url"] = parsed.get("data_url")
                        result["source_info"] = parsed
                    except json.JSONDecodeError:
                        pass

                # Fallback: extract URLs from content if not found
                urls = re.findall(r'https?://[^\s<>"\')\]]+', content)
                urls = [u.rstrip('.,)') for u in urls if len(u) > 10]

                if urls and not result.get("detected_url"):
                    result["detected_url"] = urls[0]

                if urls:
                    main_domain = re.search(r'https?://([^/]+)', urls[0])
                    main_domain = main_domain.group(1) if main_domain else ""

                    for u in urls:
                        ul = u.lower()
                        # License URL - on same domain, not external
                        if not result.get("license_url") and any(k in ul for k in ['license', 'terms', 'legal', 'policy', 'disclaimer']):
                            if 'creativecommons' not in ul:
                                result["license_url"] = u
                        # Data URL - specific pages with params or keywords
                        if not result.get("data_url") and any(k in ul for k in ['publication', 'report', 'table', 'statistics', 'handbook', 'summary', '?head=', '?templateId=', '?pid=']):
                            result["data_url"] = u

                # Filter out external license URLs from parsed result
                if result.get("license_url") and 'creativecommons.org' in result["license_url"]:
                    result["license_url"] = None

                # If we found a URL, return success
                if result.get("detected_url"):
                    result["attempts"] = attempt + 1
                    return result

            # Wait before retry with exponential backoff
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                time.sleep(wait_time)

        # All retries exhausted - return last result with attempt count
        if last_result:
            last_result["attempts"] = max_retries
            last_result["error"] = f"Could not find URL after {max_retries} attempts"
        return last_result or {"success": False, "error": f"Could not find URL after {max_retries} attempts", "attempts": max_retries}

    def extract_all_metadata(self, url: str, max_retries: int = 2, description: str = None) -> dict:
        """Extract all metadata types using a single browser automation query.

        This is more efficient than calling individual extractors as it uses
        the parallel browser capabilities to gather all information at once.

        Args:
            url: Dataset or website URL
            max_retries: Maximum retry attempts (default: 2)
            description: User-provided description of what to look for

        Returns:
            dict with all metadata types
        """
        desc_context = f"\n\nUSER REQUEST: {description}\n" if description else ""
        query = f"""Analyze this data source: {url}{desc_context}

Return a STRUCTURED report with these sections:

## 1. DATA CATALOG LINKS (10+ links)
Find and list ALL available dataset pages, data tables, and download links:
| Dataset Name | URL | Description |
|--------------|-----|-------------|
| ... | https://... | Brief description |

Include: data catalogs, specific datasets, CSV/API endpoints, statistical tables.

## 2. LICENSE & TERMS
- **License Type:** (e.g., CC-BY-4.0, Open Government License)
- **License URL:** Direct link to terms page
- **Attribution:** Required citation format
- **Restrictions:** Any usage limitations

## 3. GEOGRAPHIC COVERAGE
- **Countries/Regions:** List all covered areas
- **Place Types:** Country, State, City, PostalCode, etc.
- **Place ID System:** ISO 3166, FIPS, custom codes
- **Resolution:** National, regional, local level

## 4. TEMPORAL COVERAGE
- **Date Range:** Start year - End year
- **Update Frequency:** Daily/Monthly/Annual
- **Last Updated:** Most recent update date

## 5. API & TECHNICAL ACCESS
- **API Endpoint:** URL if available
- **Data Formats:** CSV, JSON, XML, etc.
- **Documentation:** Link to API docs

Browse multiple pages to find comprehensive information. Prioritize finding actual data download links."""

        result = self.extract_with_automation(query, max_retries=max_retries)

        if result["success"]:
            result["parsed_metadata"] = {
                "license": self._parse_license_content(result["content"]),
                "place": self._parse_place_content(result["content"]),
                "temporal": self._parse_temporal_content(result["content"])
            }

        return result

    def _parse_license_content(self, content: str) -> dict:
        """Parse license information from response content."""
        import re
        from urllib.parse import urlparse

        license_data = {
            "license_type": None,
            "license_url": None,
            "attribution": None,
            "restrictions": None,
            "confidence": None
        }

        if not content:
            return license_data

        def is_valid_license_url(url: str) -> bool:
            """Validate if URL is likely a license/terms page."""
            if not url:
                return False

            url_lower = url.lower()
            parsed = urlparse(url_lower)
            path = parsed.path

            # Keywords that indicate a license/terms page
            license_keywords = [
                'license', 'licence', 'terms', 'legal', 'copyright',
                'conditions', 'policy', 'privacy', 'disclaimer', 'tos',
                'eula', 'agreement', 'rights', 'usage', 'creative-commons',
                'creativecommons', 'cc-by', 'open-data', 'opendata'
            ]

            # Check if URL path contains license-related keywords
            if any(kw in path for kw in license_keywords):
                return True

            # Check for known license domains
            license_domains = [
                'creativecommons.org', 'opensource.org', 'gnu.org/licenses',
                'choosealicense.com', 'spdx.org'
            ]
            if any(domain in url_lower for domain in license_domains):
                return True

            # Reject URLs that are clearly not license pages
            reject_patterns = [
                r'/$',  # Homepage (ends with just /)
                r'/data/?$', r'/dataset', r'/table', r'/statistics',
                r'/news', r'/press', r'/contact', r'/about/?$',
                r'/search', r'/login', r'/register', r'/api/',
                r'\.(csv|xlsx|json|xml|zip|pdf)$'  # Data files
            ]
            for pattern in reject_patterns:
                if re.search(pattern, path):
                    return False

            # If path is very short (likely homepage), reject
            if len(path.strip('/')) < 3:
                return False

            return True

        # Extract URL first (before lowercasing) using regex
        # Look for explicitly labeled license URL
        url_match = re.search(r'license\s*(?:url|link)[:\s]*\(?(https?://[^\s<>"\')\]]+)', content, re.IGNORECASE)
        candidate_url = None

        if url_match:
            candidate_url = url_match.group(1).rstrip('.,')
        else:
            # Fallback: find any URL near license-related text
            license_section = re.search(r'(?:license|licensing|terms)[^}]{0,300}?(https?://[^\s<>"\')\]]+)', content, re.IGNORECASE)
            if license_section:
                candidate_url = license_section.group(1).rstrip('.,')

        # Validate the URL before accepting it
        if candidate_url and is_valid_license_url(candidate_url):
            license_data['license_url'] = candidate_url
        elif candidate_url:
            # URL found but doesn't look like a license page - don't include it
            license_data['license_url'] = None

        # Now lowercase for other extractions
        lines = content.lower().split('\n')
        for line in lines:
            if 'license type' in line or ('license:' in line and 'url' not in line):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    value = parts[1].strip()
                    # Don't set license type if it looks like "not found"
                    if 'not found' not in value and 'n/a' not in value:
                        license_data['license_type'] = value
            elif 'confidence' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    license_data['confidence'] = parts[1].strip()

        return license_data

    def _parse_place_content(self, content: str) -> dict:
        """Parse place information from response content."""
        place_data = {
            "geographic_coverage": {},
            "place_types": [],
            "place_id_systems": {},
            "spatial_resolution": None
        }

        # Basic parsing logic
        return place_data

    def _parse_temporal_content(self, content: str) -> dict:
        """Parse temporal information from response content."""
        temporal_data = {
            "coverage_period": {},
            "update_frequency": {},
            "temporal_resolution": None,
            "data_type": None
        }

        # Basic parsing logic
        return temporal_data
