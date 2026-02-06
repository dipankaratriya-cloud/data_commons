#!/usr/bin/env python3
"""Streamlit app for comprehensive metadata extraction using Browser Automation.

This app uses Groq's browser automation capabilities to search through
web pages and nested links to find:
- License information
- Place types and Place IDs
- Date range / Temporal coverage
- Geographic coverage
"""

import streamlit as st
import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from src.utils.groq_browser_automation import GroqBrowserAutomation


def search_statistical_variables(query: str, api_key: str = None) -> dict:
    """Search Data Commons for statistical variables and return their constraint properties."""
    api_key = api_key or os.getenv("DC_API_KEY")
    headers = {"X-API-Key": api_key} if api_key else {}

    try:
        # Build potential DCID patterns from query
        query_clean = query.strip().title().replace(" ", "")
        patterns = [
            f"Count_{query_clean}", f"Count_Person_{query_clean}", f"Area_{query_clean}",
            f"Amount_{query_clean}", f"Percent_{query_clean}", f"Number_{query_clean}",
            f"Count_Establishment_{query_clean}", f"Count_Worker_{query_clean}",
            f"Count_CivicStructure_{query_clean}Facility", f"Count_Farm",
            f"Area_Farm", f"Amount_FarmInventory", f"Percent_Farm",
        ]

        # Also try SPARQL search
        sparql_query = f'''
SELECT DISTINCT ?dcid WHERE {{
  ?dcid typeOf StatisticalVariable .
  FILTER(CONTAINS(LCASE(STR(?dcid)), "{query.lower()}"))
}} LIMIT 20
'''
        sparql_dcids = []
        try:
            resp = requests.get(
                "https://api.datacommons.org/v2/sparql",
                headers=headers,
                params={"query": sparql_query},
                timeout=15
            )
            if resp.status_code == 200:
                for row in resp.json().get("rows", []):
                    cells = row.get("cells", [])
                    if cells:
                        sparql_dcids.append(cells[0].get("value", ""))
        except:
            pass

        # Combine patterns and SPARQL results
        all_dcids = list(set(patterns + sparql_dcids))

        # Fetch properties for potential DCIDs
        results = []
        # Check in batches
        for i in range(0, len(all_dcids), 10):
            batch = all_dcids[i:i+10]
            props_resp = requests.post(
                "https://api.datacommons.org/v2/node",
                headers=headers,
                json={"nodes": batch, "property": "->*"},
                timeout=15
            )
            if props_resp.status_code == 200:
                data = props_resp.json().get("data", {})
                for dcid, info in data.items():
                    arcs = info.get("arcs", {})
                    if arcs:  # Only include if it has properties (exists)
                        props = {}
                        for k, v in arcs.items():
                            values = [n.get("value") or n.get("dcid") for n in v.get("nodes", [])]
                            if values:
                                props[k] = values
                        if props:
                            results.append({"dcid": dcid, "properties": props, "url": f"https://datacommons.org/browser/{dcid}"})

        if not results:
            return {"success": False, "error": f"No statistical variables found for '{query}'"}

        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}


def find_dc_property(query: str, api_key: str = None) -> dict:
    """Find Data Commons property for a concept (e.g., 'agriculture' -> 'economicSector, Agriculture')."""
    api_key = api_key or os.getenv("DC_API_KEY")
    if not api_key:
        return {"success": False, "error": "DC_API_KEY required"}

    headers = {"X-API-Key": api_key}
    query_lower = query.lower().strip()

    try:
        # Search for matching entities using SPARQL
        sparql = f"""
        SELECT ?dcid ?name ?type WHERE {{
            ?dcid name ?name .
            ?dcid typeOf ?type .
            FILTER(CONTAINS(LCASE(?name), "{query_lower}") || CONTAINS(LCASE(STR(?dcid)), "{query_lower}"))
        }} LIMIT 20
        """
        resp = requests.get(
            "https://api.datacommons.org/v2/sparql",
            headers=headers,
            params={"query": sparql},
            timeout=30
        )
        results = []
        if resp.status_code == 200:
            data = resp.json()
            for row in data.get("rows", []):
                cells = row.get("cells", [])
                if len(cells) >= 3:
                    dcid = cells[0].get("value", "")
                    name = cells[1].get("value", "")
                    type_val = cells[2].get("value", "")
                    # Extract property from type (e.g., EconomicSectorEnum -> economicSector)
                    if "Enum" in type_val:
                        prop = type_val.replace("Enum", "")
                        prop = prop[0].lower() + prop[1:] if prop else prop
                        results.append({"property": prop, "value": name, "dcid": dcid, "type": type_val})

        # Also try direct node lookup for enum values
        resp2 = requests.post(
            "https://api.datacommons.org/v2/node",
            headers=headers,
            json={"nodes": [query, query.title(), f"dc/{query}"], "property": "->*"},
            timeout=30
        )
        if resp2.status_code == 200:
            for node_id, node_data in resp2.json().get("data", {}).items():
                arcs = node_data.get("arcs", {})
                type_of = arcs.get("typeOf", {}).get("nodes", [])
                for t in type_of:
                    type_val = t.get("dcid", "")
                    if "Enum" in type_val:
                        prop = type_val.replace("Enum", "")
                        prop = prop[0].lower() + prop[1:] if prop else prop
                        name = arcs.get("name", {}).get("nodes", [{}])[0].get("value", node_id)
                        results.append({"property": prop, "value": name, "dcid": node_id, "type": type_val})

        if results:
            # Deduplicate
            seen = set()
            unique = []
            for r in results:
                key = (r["property"], r["value"])
                if key not in seen:
                    seen.add(key)
                    unique.append(r)
            return {"success": True, "results": unique}
        return {"success": False, "error": f"No DC property found for '{query}'"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_entity_properties(entity_name: str, api_key: str = None) -> dict:
    """Fetch Data Commons properties for an entity by name - supports places, statistical variables, topics, etc."""
    api_key = api_key or os.getenv("DC_API_KEY")
    if not api_key:
        return {"success": False, "error": "Data Commons API key required. Get one free at apikeys.datacommons.org and add DC_API_KEY to .env"}

    headers = {"X-API-Key": api_key}

    def try_resolve(nodes, prop):
        """Try to resolve entity with given property."""
        try:
            resp = requests.post(
                "https://api.datacommons.org/v2/resolve",
                headers=headers,
                json={"nodes": nodes, "property": prop},
                timeout=30
            )
            data = resp.json()
            entities = data.get("entities", [])
            if entities and entities[0].get("candidates"):
                return entities[0]["candidates"]
        except:
            pass
        return []

    def search_statistical_variables(query):
        """Search for statistical variables matching the query."""
        try:
            # Search for statistical variables
            resp = requests.get(
                f"https://api.datacommons.org/v2/node",
                headers=headers,
                params={
                    "nodes": "dc/g/Root",
                    "property": "->member"
                },
                timeout=30
            )
            # Try the search API for variables
            search_resp = requests.get(
                f"https://datacommons.org/api/explore/search?query={requests.utils.quote(query)}",
                timeout=30
            )
            if search_resp.status_code == 200:
                data = search_resp.json()
                if data.get("variables"):
                    return [{"dcid": v} for v in data["variables"][:10]]
        except:
            pass
        return []

    try:
        candidates = []

        # Method 1: Try direct DCID lookup first (if user entered a DCID)
        if "/" in entity_name or entity_name.startswith("dc/"):
            dcid = entity_name
            props_resp = requests.post(
                "https://api.datacommons.org/v2/node",
                headers=headers,
                json={"nodes": [dcid], "property": "->*"},
                timeout=30
            )
            data = props_resp.json().get("data", {})
            if dcid in data:
                arcs = data.get(dcid, {}).get("arcs", {})
                props = {k: [n.get("value") or n.get("dcid") for n in v.get("nodes", [])] for k, v in arcs.items()}
                return {"success": True, "dcid": dcid, "name": entity_name, "properties": props, "all_candidates": [dcid], "entity_type": "Direct DCID"}

        # Method 2: Try description property
        candidates = try_resolve([entity_name], "<-description->dcid")

        # Method 3: Try name property
        if not candidates:
            candidates = try_resolve([entity_name], "<-name->dcid")

        # Method 4: Search for StatisticalVariable
        if not candidates:
            try:
                # Try to find statistical variables with this name
                sv_search = requests.post(
                    "https://api.datacommons.org/v2/resolve",
                    headers=headers,
                    json={"nodes": [entity_name], "property": "<-name{typeOf:StatisticalVariable}->dcid"},
                    timeout=30
                )
                sv_data = sv_search.json()
                entities = sv_data.get("entities", [])
                if entities and entities[0].get("candidates"):
                    candidates = entities[0]["candidates"]
            except:
                pass

        # Method 5: Search Data Commons explore API for variables
        if not candidates:
            try:
                explore_resp = requests.get(
                    f"https://datacommons.org/api/explore/search?query={requests.utils.quote(entity_name)}",
                    timeout=30
                )
                if explore_resp.status_code == 200:
                    explore_data = explore_resp.json()
                    if explore_data.get("variables"):
                        candidates = [{"dcid": v} for v in explore_data["variables"][:10]]
            except:
                pass

        # Method 6: Try the v2 observation endpoint to find related variables
        if not candidates:
            try:
                # Search using autocomplete-like functionality
                auto_resp = requests.get(
                    f"https://api.datacommons.org/v2/sparql",
                    headers=headers,
                    params={
                        "query": f"""
                        SELECT ?dcid ?name WHERE {{
                            ?dcid typeOf StatisticalVariable .
                            ?dcid name ?name .
                            FILTER(CONTAINS(LCASE(?name), "{entity_name.lower()}"))
                        }}
                        LIMIT 10
                        """
                    },
                    timeout=30
                )
                if auto_resp.status_code == 200:
                    sparql_data = auto_resp.json()
                    rows = sparql_data.get("rows", [])
                    if rows:
                        candidates = [{"dcid": row.get("cells", [{}])[0].get("value")} for row in rows if row.get("cells")]
            except:
                pass

        # Method 7: Use find API for Places
        if not candidates:
            try:
                find_resp = requests.get(
                    f"https://api.datacommons.org/v2/find?query={requests.utils.quote(entity_name)}&type=Place",
                    headers=headers,
                    timeout=30
                )
                find_data = find_resp.json()
                items = find_data.get("items", [])
                if items:
                    candidates = [{"dcid": item.get("dcid")} for item in items if item.get("dcid")]
            except:
                pass

        # Method 8: Use find API without type constraint
        if not candidates:
            try:
                find_resp = requests.get(
                    f"https://api.datacommons.org/v2/find?query={requests.utils.quote(entity_name)}",
                    headers=headers,
                    timeout=30
                )
                find_data = find_resp.json()
                items = find_data.get("items", [])
                if items:
                    candidates = [{"dcid": item.get("dcid")} for item in items if item.get("dcid")]
            except:
                pass

        if not candidates:
            return {"success": False, "error": f"Could not resolve '{entity_name}' to a Data Commons entity. Try:\n- Places: 'France', 'California', 'Paris'\n- Variables: 'population', 'gdp', 'unemployment'\n- DCIDs: 'country/USA', 'Count_Person'"}

        dcid = candidates[0]["dcid"]
        all_dcids = [c["dcid"] for c in candidates[:10] if c.get("dcid")]

        # Fetch properties for the found entity
        props_resp = requests.post(
            "https://api.datacommons.org/v2/node",
            headers=headers,
            json={"nodes": [dcid], "property": "->*"},
            timeout=30
        )
        arcs = props_resp.json().get("data", {}).get(dcid, {}).get("arcs", {})
        props = {k: [n.get("value") or n.get("dcid") for n in v.get("nodes", [])] for k, v in arcs.items()}

        # Determine entity type from properties
        entity_type = "Unknown"
        if "typeOf" in props:
            entity_type = ", ".join(str(t) for t in props["typeOf"][:3])

        return {"success": True, "dcid": dcid, "name": entity_name, "properties": props, "all_candidates": all_dcids, "entity_type": entity_type}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Country name to Data Commons DCID mapping
COUNTRY_DCIDS = {
    "united states": "country/USA", "usa": "country/USA", "us": "country/USA", "america": "country/USA",
    "canada": "country/CAN", "france": "country/FRA", "french": "country/FRA",
    "norway": "country/NOR", "norwegian": "country/NOR", "united kingdom": "country/GBR",
    "uk": "country/GBR", "great britain": "country/GBR", "england": "country/GBR",
    "germany": "country/DEU", "german": "country/DEU", "spain": "country/ESP", "spanish": "country/ESP",
    "italy": "country/ITA", "italian": "country/ITA", "japan": "country/JPN", "japanese": "country/JPN",
    "china": "country/CHN", "chinese": "country/CHN", "india": "country/IND", "indian": "country/IND",
    "australia": "country/AUS", "australian": "country/AUS", "brazil": "country/BRA", "brazilian": "country/BRA",
    "mexico": "country/MEX", "mexican": "country/MEX", "russia": "country/RUS", "russian": "country/RUS",
    "south korea": "country/KOR", "korea": "country/KOR", "netherlands": "country/NLD", "dutch": "country/NLD",
    "sweden": "country/SWE", "swedish": "country/SWE", "switzerland": "country/CHE", "swiss": "country/CHE",
    "belgium": "country/BEL", "austria": "country/AUT", "poland": "country/POL", "denmark": "country/DNK",
    "finland": "country/FIN", "ireland": "country/IRL", "portugal": "country/PRT", "greece": "country/GRC",
    "new zealand": "country/NZL", "singapore": "country/SGP", "south africa": "country/ZAF",
    "argentina": "country/ARG", "chile": "country/CHL", "colombia": "country/COL", "peru": "country/PER",
    "indonesia": "country/IDN", "malaysia": "country/MYS", "thailand": "country/THA", "vietnam": "country/VNM",
    "philippines": "country/PHL", "egypt": "country/EGY", "nigeria": "country/NGA", "kenya": "country/KEN",
    "israel": "country/ISR", "saudi arabia": "country/SAU", "turkey": "country/TUR", "ukraine": "country/UKR",
    "czech republic": "country/CZE", "czechia": "country/CZE", "hungary": "country/HUN", "romania": "country/ROU",
    "bulgaria": "country/BGR", "bulgarian": "country/BGR", "croatia": "country/HRV", "slovakia": "country/SVK",
    "slovenia": "country/SVN", "estonia": "country/EST", "latvia": "country/LVA", "lithuania": "country/LTU",
}

def get_country_dcids(text: str) -> list:
    """Extract Data Commons DCIDs for countries mentioned in text.
    Returns list of tuples: (country_name, dcid)
    """
    if not text:
        return []
    text_lower = text.lower()
    found = []
    seen_dcids = set()
    for name, dcid in COUNTRY_DCIDS.items():
        if name in text_lower and dcid not in seen_dcids:
            # Get proper country name (first entry for this DCID)
            country_name = name.title()
            found.append((country_name, dcid))
            seen_dcids.add(dcid)
    return found

# Load environment variables from .env file in script directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)


def format_comprehensive_display(result: dict):
    """Format and display all metadata extraction results in Streamlit."""
    if not result.get("success"):
        st.error(f"Error: {result.get('error', 'Unknown error')}")
        return

    # Create tabs for different metadata types
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Summary",
        "License",
        "Place/Geographic",
        "Date Range/Temporal",
        "Browser Sessions"
    ])

    # Parse metadata
    parsed = result.get("parsed_metadata", {})

    # Summary Tab
    with tab1:
        st.subheader("Complete Extracted Information")
        content = result.get("content", "No content available")
        # Inject Data Commons DCID into geographic coverage section
        country_dcids = get_country_dcids(content)
        if country_dcids and "GEOGRAPHIC COVERAGE" in content.upper():
            dcid_entries = [f"{name}: `{dcid}`" for name, dcid in country_dcids]
            dcid_line = f"\n- **Data Commons DCIDs:** {', '.join(dcid_entries)}"
            # Insert after geographic coverage section header
            import re
            content = re.sub(r'(#+\s*\d*\.?\s*GEOGRAPHIC COVERAGE[^\n]*\n)', r'\1' + dcid_line + '\n', content, flags=re.IGNORECASE)
        st.markdown(content)

    # License Tab
    with tab2:
        st.subheader("License Information")
        license_data = parsed.get("license", {})

        if license_data.get("license_type") or license_data.get("license_url"):
            col1, col2 = st.columns(2)

            with col1:
                if license_data.get("license_type"):
                    st.metric("License Type", license_data["license_type"])
                if license_data.get("confidence"):
                    confidence = license_data["confidence"]
                    st.metric("Confidence", confidence.capitalize())

            with col2:
                if license_data.get("license_url"):
                    st.markdown("**License URL:**")
                    st.markdown(f"[{license_data['license_url']}]({license_data['license_url']})")

            if license_data.get("attribution"):
                st.markdown("**Attribution Requirements:**")
                st.info(license_data["attribution"])

            if license_data.get("restrictions"):
                st.markdown("**Usage Restrictions:**")
                st.warning(license_data["restrictions"])
        else:
            st.info("No license information found in the extracted metadata")

    # Place Tab
    with tab3:
        st.subheader("Geographic & Place Information")
        place_data = parsed.get("place", {})

        # Geographic Coverage
        geo_coverage = place_data.get("geographic_coverage", {})
        all_geo_text = ""
        if geo_coverage:
            st.markdown("**Geographic Coverage:**")
            for key, value in geo_coverage.items():
                if value:
                    st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
                    all_geo_text += f" {value}"
        # Also check full content for country mentions
        all_geo_text += f" {result.get('content', '')}"
        country_dcids = get_country_dcids(all_geo_text)
        if country_dcids:
            st.markdown("**Data Commons Country DCIDs:**")
            for country_name, dcid in country_dcids:
                st.write(f"• {country_name}: `{dcid}`")

        # Place Types
        place_types = place_data.get("place_types", [])
        if place_types:
            st.markdown("**Place Types:**")
            cols = st.columns(min(3, len(place_types)))
            for idx, place_type in enumerate(place_types):
                with cols[idx % 3]:
                    st.info(place_type)

        # Place ID Systems
        id_systems = place_data.get("place_id_systems", {})
        if id_systems:
            st.markdown("**Place ID Systems:**")
            for key, value in id_systems.items():
                if value:
                    st.write(f"• **{key.replace('_', ' ').title()}:** {value}")

        # Spatial Resolution
        if place_data.get("spatial_resolution"):
            st.markdown("**Spatial Resolution:**")
            st.success(place_data["spatial_resolution"])

        if not any([geo_coverage, place_types, id_systems, place_data.get("spatial_resolution")]):
            st.info("No place/geographic information found in the extracted metadata")

    # Temporal Tab
    with tab4:
        st.subheader("Temporal & Date Range Information")
        temporal_data = parsed.get("temporal", {})

        # Coverage Period
        coverage = temporal_data.get("coverage_period", {})
        if coverage:
            st.markdown("**Coverage Period:**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Start Date", coverage.get("start_date", "N/A"))
            with col2:
                st.metric("End Date", coverage.get("end_date", "N/A"))

        # Update Information
        update_info = temporal_data.get("update_frequency", {})
        if update_info:
            st.markdown("**Update Information:**")
            for key, value in update_info.items():
                if value:
                    st.write(f"• **{key.replace('_', ' ').title()}:** {value}")

        # Temporal Resolution
        if temporal_data.get("temporal_resolution"):
            st.markdown("**Temporal Resolution:**")
            st.info(temporal_data["temporal_resolution"])

        # Data Type
        if temporal_data.get("data_type"):
            st.markdown("**Data Type:**")
            st.success(temporal_data["data_type"])

        if not any([coverage, update_info, temporal_data.get("temporal_resolution"), temporal_data.get("data_type")]):
            st.info("No temporal/date range information found in the extracted metadata")

    # Browser Sessions Tab
    with tab5:
        st.subheader("Browser Automation Details")

        if result.get("executed_tools"):
            st.info(f"Launched {len(result['executed_tools'])} browser session(s) to gather comprehensive information")

            for i, tool in enumerate(result["executed_tools"], 1):
                # Handle both dict and object types
                if hasattr(tool, 'type'):
                    tool_type = getattr(tool, 'type', 'unknown')
                    tool_output = getattr(tool, 'output', None)
                else:
                    tool_type = tool.get('type', 'unknown') if isinstance(tool, dict) else 'unknown'
                    tool_output = tool.get('output') if isinstance(tool, dict) else None

                with st.expander(f"Session {i}: {tool_type}", expanded=False):
                    st.markdown(f"**Type:** `{tool_type}`")
                    if tool_output:
                        output_preview = str(tool_output)[:500]
                        st.text_area("Output", output_preview, height=150, key=f"tool_{i}")
        else:
            st.warning("No browser automation session data available")

        # Display reasoning
        if result.get("reasoning"):
            st.markdown("---")
            st.subheader("Browser Automation Reasoning")
            st.caption("How the browser automation navigated and extracted information")
            with st.expander("View Detailed Reasoning Process", expanded=False):
                st.text_area("Decision-Making Process", result["reasoning"], height=300, key="reasoning")


def save_results_json(result: dict, url: str):
    """Save results to JSON file and provide download button."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_url = url.replace("https://", "").replace("http://", "").replace("/", "_")[:50]
    filename = f"metadata_extraction_{safe_url}_{timestamp}.json"

    # Convert executed_tools to serializable format
    executed_tools = result.get("executed_tools", [])
    serializable_tools = []

    if executed_tools:
        for tool in executed_tools:
            if hasattr(tool, '__dict__'):
                # Convert object to dict
                tool_dict = {
                    'type': getattr(tool, 'type', None),
                    'output': str(getattr(tool, 'output', ''))[:1000] if getattr(tool, 'output', None) else None,
                    'name': getattr(tool, 'name', None),
                }
                serializable_tools.append(tool_dict)
            elif isinstance(tool, dict):
                serializable_tools.append(tool)
            else:
                serializable_tools.append({'type': str(type(tool)), 'value': str(tool)})

    output_data = {
        "url": url,
        "extraction_type": "comprehensive_metadata",
        "timestamp": datetime.now().isoformat(),
        "result": {
            "success": result.get("success"),
            "content": result.get("content"),
            "parsed_metadata": result.get("parsed_metadata"),
            "license_data": result.get("license_data"),
            "place_data": result.get("place_data"),
            "temporal_data": result.get("temporal_data"),
            "reasoning": result.get("reasoning"),
            "executed_tools": serializable_tools,
            "error": result.get("error")
        }
    }

    json_str = json.dumps(output_data, indent=2, ensure_ascii=False, default=str)

    st.download_button(
        label="Download Results as JSON",
        data=json_str,
        file_name=filename,
        mime="application/json",
        use_container_width=True
    )


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Metadata Extractor - Browser Automation",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS for clean light theme
    st.markdown("""
        <style>
        /* ===== COLOR PALETTE =====
        Primary: #2563eb (Blue)
        Background: #ffffff (White)
        Text: #000000 (Black)
        Border: #d1d5db (Gray 300)
        */

        /* Main background and text */
        .stApp {
            background-color: #ffffff;
            color: #000000;
        }

        /* All text elements */
        p, span, div, label, li {
            color: #000000 !important;
        }

        /* Strong/Bold text */
        strong, b {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        /* Links */
        a {
            color: #2563eb !important;
            text-decoration: none !important;
        }

        a:hover {
            color: #1d4ed8 !important;
            text-decoration: underline !important;
        }

        /* Headers */
        h1 {
            color: #000000 !important;
            font-weight: 700 !important;
            font-size: 2.25rem !important;
        }

        h2 {
            color: #000000 !important;
            font-weight: 600 !important;
            font-size: 1.875rem !important;
        }

        h3 {
            color: #000000 !important;
            font-weight: 600 !important;
            font-size: 1.5rem !important;
        }

        h4, h5, h6 {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        /* Captions and small text */
        .stCaptionContainer, [data-testid="stCaptionContainer"] {
            color: #000000 !important;
        }

        /* Code blocks */
        code {
            background-color: #f3f4f6 !important;
            color: #000000 !important;
            padding: 0.2rem 0.4rem !important;
            border-radius: 0.25rem !important;
            font-size: 0.875rem !important;
        }

        pre {
            background-color: #f9fafb !important;
            border: 1px solid #d1d5db !important;
            border-radius: 0.5rem !important;
            padding: 1rem !important;
        }

        pre code {
            background-color: transparent !important;
            color: #000000 !important;
        }

        /* Success messages */
        div[data-baseweb="notification"][kind="success"] {
            background-color: #f0fdf4 !important;
            border-left: 4px solid #22c55e !important;
        }

        div[data-baseweb="notification"][kind="success"] p,
        div[data-baseweb="notification"][kind="success"] div {
            color: #000000 !important;
        }

        /* Error messages */
        div[data-baseweb="notification"][kind="error"] {
            background-color: #fef2f2 !important;
            border-left: 4px solid #ef4444 !important;
        }

        div[data-baseweb="notification"][kind="error"] p,
        div[data-baseweb="notification"][kind="error"] div {
            color: #000000 !important;
        }

        /* Warning messages */
        div[data-baseweb="notification"][kind="warning"] {
            background-color: #fffbeb !important;
            border-left: 4px solid #f59e0b !important;
        }

        div[data-baseweb="notification"][kind="warning"] p,
        div[data-baseweb="notification"][kind="warning"] div {
            color: #000000 !important;
        }

        /* Info messages */
        div[data-baseweb="notification"][kind="info"] {
            background-color: #eff6ff !important;
            border-left: 4px solid #3b82f6 !important;
        }

        div[data-baseweb="notification"][kind="info"] p,
        div[data-baseweb="notification"][kind="info"] div {
            color: #000000 !important;
        }

        /* Buttons */
        .stButton > button {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1.5px solid #d1d5db !important;
            font-weight: 500 !important;
            border-radius: 0.5rem !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.2s !important;
        }

        .stButton > button:hover {
            background-color: #f9fafb !important;
            border-color: #9ca3af !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        }

        /* Primary button */
        .stButton > button[kind="primary"] {
            background-color: #2563eb !important;
            color: #ffffff !important;
            border: 1.5px solid #2563eb !important;
            font-weight: 600 !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #1d4ed8 !important;
            border-color: #1d4ed8 !important;
            box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2) !important;
        }

        /* Download button */
        .stDownloadButton > button {
            background-color: #10b981 !important;
            color: #ffffff !important;
            border: 1.5px solid #10b981 !important;
            font-weight: 600 !important;
            border-radius: 0.5rem !important;
        }

        .stDownloadButton > button:hover {
            background-color: #059669 !important;
            border-color: #059669 !important;
            box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2) !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #ffffff !important;
            border-bottom: 2px solid #d1d5db !important;
            padding: 0 0.5rem !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: #000000 !important;
            background-color: transparent !important;
            border: none !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 500 !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #000000 !important;
            background-color: #f9fafb !important;
        }

        .stTabs [aria-selected="true"] {
            color: #000000 !important;
            border-bottom: 3px solid #2563eb !important;
            font-weight: 600 !important;
        }

        /* Input fields */
        .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1.5px solid #d1d5db !important;
            border-radius: 0.5rem !important;
            padding: 0.625rem 0.75rem !important;
            font-size: 0.9375rem !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        }

        .stTextInput > label {
            color: #000000 !important;
            font-weight: 500 !important;
        }

        /* Text areas */
        .stTextArea textarea {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1.5px solid #d1d5db !important;
            border-radius: 0.5rem !important;
            padding: 0.75rem !important;
        }

        .stTextArea textarea:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #f9fafb !important;
            border-right: 1px solid #d1d5db !important;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] label {
            color: #000000 !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #d1d5db !important;
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
        }

        .streamlit-expanderHeader:hover {
            background-color: #f9fafb !important;
            border-color: #9ca3af !important;
        }

        .streamlit-expanderContent {
            background-color: #ffffff !important;
            border: 1px solid #d1d5db !important;
            border-top: none !important;
        }

        /* Dividers */
        hr {
            border-color: #d1d5db !important;
            margin: 1.5rem 0 !important;
        }

        /* Progress bar */
        .stProgress > div > div {
            background-color: #e5e7eb !important;
        }

        .stProgress > div > div > div {
            background-color: #2563eb !important;
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        [data-testid="stMetricLabel"] {
            color: #000000 !important;
        }

        [data-testid="stMetricDelta"] {
            color: #000000 !important;
        }

        /* Markdown content */
        .stMarkdown {
            color: #000000 !important;
        }

        .stMarkdown p {
            color: #000000 !important;
            line-height: 1.6 !important;
        }

        .stMarkdown ul, .stMarkdown ol {
            color: #000000 !important;
        }

        .stMarkdown li {
            color: #000000 !important;
            margin-bottom: 0.5rem !important;
        }

        /* Checkbox */
        .stCheckbox {
            color: #000000 !important;
        }

        /* Radio */
        .stRadio label {
            color: #000000 !important;
        }

        /* Selectbox */
        .stSelectbox label {
            color: #000000 !important;
            font-weight: 500 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header with icon
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 2rem; padding: 1.5rem 0 1rem 0; border-bottom: 2px solid #d1d5db;">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2" style="margin-right: 14px;">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
            <h1 style="margin: 0; color: #000000; font-weight: 700;">Metadata Extractor</h1>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar configuration
    with st.sidebar:
        st.markdown("""
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #d1d5db;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2" style="margin-right: 10px;">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M12 1v6m0 6v6m-6-6h6m6 0h6"></path>
                    <path d="M12 1v6m0 6v6"></path>
                    <circle cx="19" cy="12" r="2"></circle>
                    <circle cx="5" cy="12" r="2"></circle>
                    <circle cx="12" cy="19" r="2"></circle>
                    <circle cx="12" cy="5" r="2"></circle>
                </svg>
                <h3 style="margin: 0; color: #000000; font-weight: 600;">Configuration</h3>
            </div>
        """, unsafe_allow_html=True)

        # API Key
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            st.error("No API key found in .env file")

        # Use default values - increased for better reliability
        model = "groq/compound"  # Use compound model for best results
        timeout = 240  # 4 minutes default (increased for complex extractions)
        max_retries = 3  # Increased retries for better reliability

        st.divider()

        # Source History
        st.markdown("""
            <div style="display: flex; align-items: center; margin: 2rem 0 1rem 0; padding-bottom: 0.75rem; border-bottom: 1px solid #d1d5db;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2" style="margin-right: 8px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <h4 style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">Recent Sources</h4>
            </div>
        """, unsafe_allow_html=True)
        if 'url_history' not in st.session_state:
            st.session_state.url_history = []

        if st.session_state.url_history:
            for idx, historic_source in enumerate(reversed(st.session_state.url_history[-5:])):
                if st.button(f"{historic_source[:40]}...", key=f"hist_{idx}", use_container_width=True):
                    st.session_state.selected_source = historic_source
                    st.rerun()
        else:
            st.info("No sources processed yet")

        st.divider()

        # Help section
        st.markdown("""
            <div style="display: flex; align-items: center; margin: 2rem 0 1rem 0; padding-bottom: 0.75rem; border-bottom: 1px solid #d1d5db;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2" style="margin-right: 8px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                <h4 style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">About</h4>
            </div>
        """, unsafe_allow_html=True)

        with st.expander("", expanded=False):
            st.markdown("""
            **What it extracts:**
            - License information
            - Geographic coverage
            - Temporal coverage

            Uses browser automation to search across multiple pages.
            """)

    # Main content area - Tool Selection Tabs
    tool_tab1, tool_tab2 = st.tabs(["Metadata Extractor", "Entity Properties"])

    with tool_tab2:
        # Entity Property Tool
        st.markdown("**Search Statistical Variables and get constraint properties**")
        entity_input = st.text_input(
            "Search term",
            placeholder="e.g., agriculture, population, income, education",
            label_visibility="collapsed",
            key="entity_input"
        )
        if st.button("Search Statistical Variables", key="get_props", use_container_width=True):
            if entity_input:
                with st.spinner("Searching Data Commons..."):
                    result = search_statistical_variables(entity_input)
                if result["success"]:
                    st.success(f"Found {len(result['results'])} statistical variables:")
                    for r in result["results"]:
                        with st.expander(f"📊 {r['dcid']}", expanded=False):
                            st.markdown(f"**[View in Browser]({r['url']})**")
                            props = r["properties"]
                            # Show key constraint properties
                            key_props = ["measuredProperty", "populationType", "statType", "measurementDenominator", "constraintProperties"]
                            for prop in key_props:
                                if prop in props:
                                    st.write(f"**{prop}:** {', '.join(str(v) for v in props[prop][:5])}")
                            # Show other properties
                            other_props = {k: v for k, v in props.items() if k not in key_props and k not in ["provenance", "typeOf"]}
                            if other_props:
                                st.markdown("**Other properties:**")
                                for k, v in list(other_props.items())[:10]:
                                    st.write(f"- {k}: {', '.join(str(x) for x in v[:3])}")
                else:
                    st.warning(result["error"])
            else:
                st.warning("Enter a search term (e.g., agriculture, population)")

    with tool_tab1:
        if not api_key:
            st.warning("Please provide a Groq API key in the sidebar or .env file")
            st.stop()

        # Source name input with icon
        st.markdown("""
            <div style="display: flex; align-items: center; margin-top: 0.5rem; margin-bottom: 0.5rem;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2" style="margin-right: 8px;">
                    <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
                <span style="color: #000000; font-size: 0.95rem; font-weight: 500;">Enter source name (URL will be auto-detected)</span>
            </div>
        """, unsafe_allow_html=True)

        default_source = st.session_state.get('selected_source', '')
        source_name = st.text_input(
            "source_input",
            value=default_source,
            placeholder="e.g., IPEDS, Statistics Canada, or https://nces.ed.gov/ipeds",
            label_visibility="collapsed"
        )

        # Description field (required for source names, optional for direct URLs)
        st.markdown("""
            <div style="display: flex; align-items: center; margin-top: 1rem; margin-bottom: 0.5rem;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2" style="margin-right: 8px;">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                </svg>
                <span style="color: #000000; font-size: 0.95rem; font-weight: 500;">Description (required for source names, optional for URLs)</span>
            </div>
        """, unsafe_allow_html=True)
        source_description = st.text_area(
            "source_description",
            placeholder="Describe what information you're looking for (e.g., 'Find license type, geographic coverage, and date range for this education dataset')",
            label_visibility="collapsed",
            height=80
        )

        # Example sources section
        with st.expander("Need an example? Try these sources"):
            st.markdown("**Government & Statistics:**")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("French Open Data", key="ex1", use_container_width=True):
                    st.session_state.selected_source = "French Open Data Portal data.gouv.fr"
                    st.rerun()
                if st.button("Norway Statistics", key="ex2", use_container_width=True):
                    st.session_state.selected_source = "Statistics Norway SSB"
                    st.rerun()

            with col2:
                if st.button("Statistics Canada", key="ex3", use_container_width=True):
                    st.session_state.selected_source = "Statistics Canada StatCan"
                    st.rerun()
                if st.button("US Census Bureau", key="ex4", use_container_width=True):
                    st.session_state.selected_source = "US Census Bureau"
                    st.rerun()

        # Extract button - full width for professional appearance
        extract_button = st.button("Extract Metadata", type="primary", use_container_width=True)

        if extract_button:
            if not source_name:
                st.warning("Please enter a source name to analyze")
                return
            # Description is required only for source names (not direct URLs)
            is_direct_url = source_name.startswith(('http://', 'https://'))
            if not is_direct_url and not source_description.strip():
                st.warning("Please enter a description of what information you're looking for")
                return

            # Add to history
            if source_name not in st.session_state.url_history:
                st.session_state.url_history.append(source_name)

            try:
                # Initialize browser automation client with timeout
                client = GroqBrowserAutomation(api_key=api_key, model=model, timeout=timeout)

                # Try extraction with timeout handling and progress tracking
                import time
                start_time = time.time()

                # Create progress indicators
                progress_bar = st.progress(0)
                status_container = st.empty()

                # Step 1: Auto-detect URL from source name (or use directly if URL provided)
                url_result = {}
                if source_name.startswith(('http://', 'https://')):
                    # User entered a URL directly
                    url = source_name
                    status_container.info(f"Using provided URL...")
                    progress_bar.progress(0.15)
                else:
                    # Search for URL
                    status_container.info(f"Searching for '{source_name}'...")
                    progress_bar.progress(0.10)
                    url_result = client.find_source_url(source_name, max_retries=max_retries)
                    url = url_result.get("detected_url")

                # Fallback: use data_url if main url not found
                if not url and url_result.get("data_url"):
                    url = url_result.get("data_url")

                if not url:
                    progress_bar.empty()
                    status_container.empty()

                    if url_result.get("error"):
                        st.error(f"API Error: {url_result.get('error')}")
                    elif url_result.get("content"):
                        st.warning("Found content but couldn't extract URL:")
                        with st.expander("Show API response"):
                            st.text(url_result.get("content", "")[:2000])
                    else:
                        st.error(f"Could not find URL for '{source_name}'")

                    st.markdown("**Try:** Enter the URL directly or use simpler search terms")
                    st.stop()

                # Show detected URLs
                st.success(f"Main Site: **{url}**")
                if url_result.get("data_url"):
                    st.success(f"Data Page: [{url_result['data_url']}]({url_result['data_url']})")
                if url_result.get("license_url"):
                    st.info(f"License Page: [{url_result['license_url']}]({url_result['license_url']})")
                progress_bar.progress(0.25)

                # Step 2: Initialize extraction
                status_container.info("Initializing browser automation (timeout: 4 minutes, max retries: 3)...")
                progress_bar.progress(0.30)
                time.sleep(0.3)

                # Step 3: Starting extraction
                status_container.info("Visiting main page and discovering links...")
                progress_bar.progress(0.40)

                # Helper function to check if result has meaningful content
                def has_meaningful_content(res):
                    """Check if the result contains actual extractable information."""
                    if not res.get("success"):
                        return False
                    content = res.get("content", "")
                    if not content or len(content.strip()) < 50:
                        return False
                    # Check if content has actual information (not just error messages)
                    content_lower = content.lower()
                    empty_indicators = [
                        "no information", "could not find", "unable to", "not available",
                        "no data", "empty", "blank", "n/a", "none found"
                    ]
                    # If content is mostly empty indicators, consider it empty
                    indicator_count = sum(1 for ind in empty_indicators if ind in content_lower)
                    if indicator_count > 3:
                        return False
                    return True

                # Actual extraction with automatic retry on failure or empty content
                max_attempts = 3
                result = None

                for attempt in range(1, max_attempts + 1):
                    status_container.info(f"Extracting metadata (attempt {attempt}/{max_attempts})...")
                    progress_bar.progress(0.30 + (attempt * 0.1))

                    result = client.extract_all_metadata(url, max_retries=max_retries, description=source_description)

                    # Check if we got meaningful content
                    if has_meaningful_content(result):
                        break

                    # If failed or empty, retry
                    if attempt < max_attempts:
                        if not result.get("success"):
                            status_container.warning(f"Attempt {attempt} failed, retrying...")
                        else:
                            status_container.warning(f"Attempt {attempt} returned empty content, retrying...")
                        time.sleep(2)

                # Final check - if still no meaningful content after all attempts
                if not has_meaningful_content(result):
                    if result.get("success"):
                        # Mark as failed if success but empty
                        result["success"] = False
                        result["error"] = "Extraction completed but returned empty or insufficient content after multiple attempts. Please try again."

                # Step 3: Processing
                status_container.info("Analyzing license and metadata information...")
                progress_bar.progress(0.70)
                time.sleep(0.2)

                # Step 4: Finalizing
                status_container.info("Finalizing extraction...")
                progress_bar.progress(0.90)
                time.sleep(0.2)

                # Complete
                progress_bar.progress(1.0)
                elapsed_time = time.time() - start_time
                status_container.empty()
                progress_bar.empty()

                # Display results
                st.divider()

                if result.get("success") and has_meaningful_content(result):
                    st.success(f"Completed in {elapsed_time:.1f}s")
                    format_comprehensive_display(result)

                    # Download button
                    st.divider()
                    save_results_json(result, url)

                else:
                    error_msg = result.get('error', 'Unknown error')

                    # Show detailed error with solutions
                    st.error("Extraction Failed")

                    # ALWAYS show the actual error first for debugging
                    st.warning(f"**Error Details:** {error_msg}")
                    st.caption("This helps us understand what went wrong")

                    # Rate limit errors (429) - HANDLE FIRST
                    if "429" in error_msg or "rate limit" in error_msg.lower() or "rate_limit_exceeded" in error_msg.lower():
                        st.markdown("""
                        **API Rate Limit Reached**

                        Your Groq API key has reached its usage limit.
                        """)

                        # Extract wait time if available
                        import re
                        wait_match = re.search(r'try again in ([\d.]+)s', error_msg)
                        if wait_match:
                            wait_time = float(wait_match.group(1))
                            st.warning(f"Wait time: **{wait_time:.1f} seconds** before the limit resets")

                        st.markdown("""
                        **Solutions:**

                        **Option 1: Wait for Rate Limit Reset (Recommended)**
                        - Wait for the time shown above
                        - Click the retry button below

                        **Option 2: Try Simpler URLs**
                        - Use main website URLs (not table views)
                        - Simpler pages use fewer tokens

                        **Option 3: Upgrade Your Plan**
                        - Visit: https://console.groq.com/settings/billing
                        - Upgrade to Dev Tier for higher limits
                        """)

                        # Show usage stats
                        usage_match = re.search(r'Limit (\d+), Used (\d+), Requested (\d+)', error_msg)
                        if usage_match:
                            limit = int(usage_match.group(1))
                            used = int(usage_match.group(2))
                            requested = int(usage_match.group(3))

                            st.markdown("**Current Usage:**")
                            usage_pct = (used / limit) * 100
                            st.progress(usage_pct / 100)
                            st.caption(f"Used: {used:,} / {limit:,} tokens ({usage_pct:.1f}%)")
                            st.caption(f"Requested: {requested:,} tokens")

                        # Auto-retry button
                        if wait_match:
                            wait_time = float(wait_match.group(1))
                            st.markdown(f"**Auto-retry in {wait_time:.0f} seconds:**")

                            col1, col2 = st.columns([2, 1])
                            with col1:
                                if st.button(f"Wait {wait_time:.0f}s and Retry", use_container_width=True, key="wait_retry"):
                                    import time
                                    with st.spinner(f"Waiting {wait_time:.0f} seconds..."):
                                        time.sleep(wait_time + 1)
                                    st.rerun()
                            with col2:
                                if st.button("Retry Now", use_container_width=True, key="retry_now"):
                                    st.rerun()

                    # Request too large errors (413)
                    elif "413" in error_msg or "too large" in error_msg.lower() or "request entity too large" in error_msg.lower():
                        st.markdown("""
                        **The page content is too large for the API to process.**

                        This happens with complex data tables or pages with lots of content.

                        **Solutions:**
                        """)

                        # Try to extract main URL
                        if "/table/" in url or "/tableView" in url:
                            parts = url.split("/")
                            main_url = "/".join(parts[:3])
                            st.markdown("1. **Try the main website instead:**")
                            if st.button(f"Try {main_url}", use_container_width=True, key="try_main"):
                                st.session_state.selected_url = main_url
                                st.rerun()
                        else:
                            st.markdown("""
                            1. **Try the homepage of the website**
                            2. **Try a simpler URL** - Avoid specific table views or large data pages
                            3. **Use the example URLs** - They're tested and work well
                            """)

                    # Timeout errors
                    elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                        st.markdown("""
                        **The extraction took too long (exceeded 3 minutes).**

                        **What you can do:**
                        1. **Try the main website URL** - If you used a specific page, try the homepage instead
                        2. **Verify the URL is accessible** - Check if the page loads in your browser
                        3. **Wait and retry** - The site may be temporarily slow
                        """)

                        if "/api/" in url:
                            main_url = url.split("/api/")[0]
                            st.info(f"**API Endpoint Detected:** Your URL contains `/api/`. Try: `{main_url}`")

                    # API endpoint errors
                    elif "/api/" in url:
                        main_url = url.split("/api/")[0]
                        st.markdown(f"**API Endpoint Detected:** Your URL appears to be an API endpoint. **Suggested URL:** `{main_url}`")
                        if st.button(f"Try {main_url}", use_container_width=True):
                            st.session_state.selected_url = main_url
                            st.rerun()

                    # Connection errors
                    elif "connection" in error_msg.lower():
                        st.markdown("""
                        **Connection Error:** Check your internet connection and verify the URL is correct.
                        """)

                    # Authentication errors
                    elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                        st.markdown("""
                        **API Key Issue:** Check your `.env` file and ensure `GROQ_API_KEY` is set correctly.
                        """)

                    # Generic errors
                    else:
                        st.markdown("**Common Solutions:** Click Extract again, wait 30 seconds, or try a different URL.")
                        if st.button("Retry Extraction", use_container_width=True):
                            st.rerun()

                    # Always show technical details in expander with full trace
                    with st.expander("Show full technical error details"):
                        st.code(error_msg)
                        st.json({
                            "success": result.get("success"),
                            "error": result.get("error"),
                            "content": result.get("content", "None")[:200] if result.get("content") else "None",
                            "reasoning": result.get("reasoning", "None")[:200] if result.get("reasoning") else "None",
                            "executed_tools": len(result.get("executed_tools", [])),
                        })

            except TimeoutError:
                st.error("Request Timed Out")
                st.markdown("**The extraction exceeded the time limit.** Try the main website URL or use one of the example URLs.")

            except Exception as e:
                st.error("An Unexpected Error Occurred")
                st.markdown("**What you can do:** Verify your API key, check your internet connection, or try a simpler URL.")
                with st.expander("Show technical error details"):
                    st.exception(e)

    # Footer
    st.divider()
    st.caption("Powered by Groq Browser Automation")


if __name__ == "__main__":
    main()
