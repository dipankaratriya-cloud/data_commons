"""Groq Browser Automation Client for advanced web research."""
import json
from groq import Groq


class GroqBrowserAutomation:
    """Client for Groq's browser automation capabilities.

    Enables launching and controlling multiple browsers simultaneously
    for comprehensive web research and metadata extraction.
    """

    def __init__(self, api_key: str, model: str = "moonshotai/kimi-k2-instruct-0905", timeout: int = 120):
        """Initialize the browser automation client.

        Args:
            api_key: Groq API key
            model: Model to use (default: moonshotai/kimi-k2-instruct-0905,
                   or groq/compound, groq/compound-mini)
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

    def extract_all_metadata(self, url: str, max_retries: int = 2) -> dict:
        """Extract all metadata types using a single browser automation query.

        This is more efficient than calling individual extractors as it uses
        the parallel browser capabilities to gather all information at once.

        Args:
            url: Dataset or website URL
            max_retries: Maximum retry attempts (default: 2)

        Returns:
            dict with all metadata types
        """
        query = f"""Analyze this dataset URL and extract comprehensive metadata: {url}

Please extract ALL of the following information:

**LICENSE INFORMATION:**
- License Type (e.g., CC-BY-4.0, MIT, Open Government License)
- License URL (direct link)
- Attribution requirements
- Usage restrictions
- Confidence level

**GEOGRAPHIC COVERAGE:**
- Countries, regions, cities covered
- Place Types (Country, State, City, etc.)
- Place ID Systems (ISO 3166, FIPS, etc.)
- Spatial Resolution
- Example place IDs

**TEMPORAL COVERAGE:**
- Coverage Period (start and end dates)
- Update Frequency
- Last Updated date
- Temporal Resolution
- Reference Period
- Data Type (historical/real-time)

Use your browser automation capabilities to search through multiple pages,
documentation, metadata sections, and related links to provide comprehensive
and accurate information. Return the information in a well-structured format."""

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
        # Basic parsing - can be enhanced with more sophisticated extraction
        license_data = {
            "license_type": None,
            "license_url": None,
            "attribution": None,
            "restrictions": None,
            "confidence": None
        }

        if not content:
            return license_data

        # Simple keyword-based extraction
        lines = content.lower().split('\n')
        for line in lines:
            if 'license type' in line or 'license:' in line:
                # Extract the value after the colon
                parts = line.split(':', 1)
                if len(parts) > 1:
                    license_data['license_type'] = parts[1].strip()
            elif 'license url' in line or 'license link' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    license_data['license_url'] = parts[1].strip()
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
