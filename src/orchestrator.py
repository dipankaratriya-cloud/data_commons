"""Orchestrator for metadata extraction with validation."""
import time
from .extractors.license_extractor import LicenseExtractor
from .extractors.place_extractor import PlaceExtractor
from .extractors.temporal_extractor import TemporalExtractor


class MetadataOrchestrator:
    """Orchestrates metadata extraction with validation."""

    def __init__(self, api_key: str):
        self.license_extractor = LicenseExtractor(api_key)
        self.place_extractor = PlaceExtractor(api_key)
        self.temporal_extractor = TemporalExtractor(api_key)

    def _validate_license(self, license_data: dict) -> dict:
        """Validate license extraction quality."""
        if not license_data or not license_data.get('success'):
            return {"quality_score": 0, "warnings": ["No license information found"]}

        best = license_data.get('best_match', {})
        score = 0
        warnings = []

        # Check for required fields
        if best.get('license_type') and best['license_type'] not in ['null', None, '']:
            score += 40
        else:
            warnings.append("License type not found")

        if best.get('license_url'):
            score += 30
        else:
            warnings.append("License URL not found")

        if best.get('attribution'):
            score += 15

        if best.get('confidence') == 'high':
            score += 15
        elif best.get('confidence') == 'medium':
            score += 7

        return {"quality_score": score, "warnings": warnings}

    def _validate_place(self, place_data: dict) -> dict:
        """Validate place extraction quality."""
        if not place_data:
            return {"quality_score": 0, "warnings": ["No place information found"]}

        score = 0
        warnings = []

        # Geographic coverage
        geo = place_data.get('geographic_coverage', {})
        if geo.get('countries'):
            score += 25
        else:
            warnings.append("Countries not found")

        if geo.get('regions'):
            score += 15

        # Place types
        if place_data.get('place_types'):
            score += 20
        else:
            warnings.append("Place types not found")

        # ID systems
        id_sys = place_data.get('place_id_systems', {})
        if id_sys.get('systems'):
            score += 20
        else:
            warnings.append("ID systems not found")

        if id_sys.get('examples') and len(id_sys['examples']) >= 3:
            score += 15

        if id_sys.get('resolution_method'):
            score += 5
        else:
            warnings.append("ID resolution method not found")

        return {"quality_score": score, "warnings": warnings}

    def _validate_temporal(self, temporal_data: dict) -> dict:
        """Validate temporal extraction quality."""
        if not temporal_data:
            return {"quality_score": 0, "warnings": ["No temporal information found"]}

        score = 0
        warnings = []

        # Coverage period
        coverage = temporal_data.get('coverage_period', {})
        if coverage.get('start_date'):
            score += 35
        else:
            warnings.append("Start date not found")

        if coverage.get('end_date'):
            score += 35
        else:
            warnings.append("End date not found")

        # Update frequency
        if temporal_data.get('update_frequency', {}).get('frequency'):
            score += 20
        else:
            warnings.append("Update frequency not found")

        # Temporal resolution
        if temporal_data.get('temporal_resolution'):
            score += 10

        return {"quality_score": score, "warnings": warnings}

    def extract_metadata(self, url: str, **kwargs) -> dict:
        """Extract all metadata from URL with validation."""
        start = time.time()

        results = {
            "url": url,
            "license": None,
            "place": None,
            "temporal": None,
            "validation": {
                "license": {},
                "place": {},
                "temporal": {},
                "overall_score": 0
            },
            "errors": [],
            "execution_time": 0
        }

        # Extract license
        try:
            results["license"] = self.license_extractor.extract(url)
            results["validation"]["license"] = self._validate_license(results["license"])
        except Exception as e:
            results["errors"].append(f"License: {str(e)}")
            results["validation"]["license"] = {"quality_score": 0, "warnings": [str(e)]}

        # Extract place
        try:
            results["place"] = self.place_extractor.extract(url)
            results["validation"]["place"] = self._validate_place(results["place"])
        except Exception as e:
            results["errors"].append(f"Place: {str(e)}")
            results["validation"]["place"] = {"quality_score": 0, "warnings": [str(e)]}

        # Extract temporal
        try:
            results["temporal"] = self.temporal_extractor.extract(url)
            results["validation"]["temporal"] = self._validate_temporal(results["temporal"])
        except Exception as e:
            results["errors"].append(f"Temporal: {str(e)}")
            results["validation"]["temporal"] = {"quality_score": 0, "warnings": [str(e)]}

        # Calculate overall quality score
        total_score = (
            results["validation"]["license"].get("quality_score", 0) +
            results["validation"]["place"].get("quality_score", 0) +
            results["validation"]["temporal"].get("quality_score", 0)
        )
        results["validation"]["overall_score"] = round(total_score / 3, 1)

        results["execution_time"] = time.time() - start
        return results
