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
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from src.utils.groq_browser_automation import GroqBrowserAutomation

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
        st.markdown(result.get("content", "No content available"))

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
        if geo_coverage:
            st.markdown("**Geographic Coverage:**")
            for key, value in geo_coverage.items():
                if value:
                    st.write(f"• **{key.replace('_', ' ').title()}:** {value}")

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
        layout="wide"
    )

    # Custom CSS for professional dark theme
    st.markdown("""
        <style>
        /* Main background and text */
        .stApp {
            background-color: #0e1117;
        }

        /* Reduce bright colors on info/success/warning/error boxes */
        .stAlert {
            background-color: rgba(50, 50, 60, 0.4) !important;
            border-left: 3px solid #4a5568 !important;
            color: #d1d5db !important;
        }

        /* Success messages - dark green */
        div[data-baseweb="notification"][kind="success"] {
            background-color: rgba(16, 55, 35, 0.6) !important;
            border-left: 3px solid #2d5f4a !important;
        }

        /* Error messages - dark red */
        div[data-baseweb="notification"][kind="error"] {
            background-color: rgba(55, 20, 20, 0.6) !important;
            border-left: 3px solid #5f2d2d !important;
        }

        /* Warning messages - dark amber */
        div[data-baseweb="notification"][kind="warning"] {
            background-color: rgba(55, 45, 20, 0.6) !important;
            border-left: 3px solid #5f4a2d !important;
        }

        /* Info messages - dark blue */
        div[data-baseweb="notification"][kind="info"] {
            background-color: rgba(20, 35, 55, 0.6) !important;
            border-left: 3px solid #2d3f5f !important;
        }

        /* Buttons - professional dark theme */
        .stButton > button {
            background-color: #1f2937 !important;
            color: #e5e7eb !important;
            border: 1px solid #374151 !important;
            font-weight: 500 !important;
        }

        .stButton > button:hover {
            background-color: #374151 !important;
            border: 1px solid #4b5563 !important;
        }

        /* Primary button */
        .stButton > button[kind="primary"] {
            background-color: #1e3a5f !important;
            border: 1px solid #2d5f8d !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #2d5f8d !important;
        }

        /* Tabs - darker theme */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1a1d24 !important;
            border-bottom: 1px solid #2d3748 !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: #9ca3af !important;
            background-color: transparent !important;
            border: none !important;
        }

        .stTabs [aria-selected="true"] {
            color: #e5e7eb !important;
            border-bottom: 2px solid #4a5568 !important;
        }

        /* Input fields */
        .stTextInput > div > div > input {
            background-color: #1f2937 !important;
            color: #e5e7eb !important;
            border: 1px solid #374151 !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0a0d12 !important;
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #d1d5db !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background-color: #1a1d24 !important;
            color: #d1d5db !important;
            border: 1px solid #2d3748 !important;
        }

        /* Text areas */
        .stTextArea textarea {
            background-color: #1f2937 !important;
            color: #e5e7eb !important;
            border: 1px solid #374151 !important;
        }

        /* Download button */
        .stDownloadButton > button {
            background-color: #1e3a5f !important;
            color: #e5e7eb !important;
            border: 1px solid #2d5f8d !important;
        }

        .stDownloadButton > button:hover {
            background-color: #2d5f8d !important;
        }

        /* Headers */
        h1, h2, h3 {
            color: #e5e7eb !important;
        }

        /* Captions */
        .caption {
            color: #9ca3af !important;
        }

        /* Dividers */
        hr {
            border-color: #2d3748 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header with icon
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#e5e7eb" stroke-width="2" style="margin-right: 12px;">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
            <h1 style="margin: 0; color: #e5e7eb;">Metadata Extractor</h1>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Extract license, place, and temporal metadata from any URL")

    # Sidebar configuration
    with st.sidebar:
        st.markdown("""
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2" style="margin-right: 8px;">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M12 1v6m0 6v6m-6-6h6m6 0h6"></path>
                    <path d="M12 1v6m0 6v6"></path>
                    <circle cx="19" cy="12" r="2"></circle>
                    <circle cx="5" cy="12" r="2"></circle>
                    <circle cx="12" cy="19" r="2"></circle>
                    <circle cx="12" cy="5" r="2"></circle>
                </svg>
                <h3 style="margin: 0; color: #e5e7eb;">Configuration</h3>
            </div>
        """, unsafe_allow_html=True)

        # API Key
        api_key = os.getenv('GROQ_API_KEY')
        if api_key:
            st.success(f"API Key loaded from environment (...{api_key[-4:]})")
        else:
            st.error("No API key found in .env file")

        # Use default values - increased for better reliability
        model = "groq/compound"  # Use compound model for best results
        timeout = 240  # 4 minutes default (increased for complex extractions)
        max_retries = 3  # Increased retries for better reliability

        st.divider()

        # URL History
        st.markdown("""
            <div style="display: flex; align-items: center; margin: 1.5rem 0 1rem 0;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2" style="margin-right: 8px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <h3 style="margin: 0; color: #e5e7eb;">Recent URLs</h3>
            </div>
        """, unsafe_allow_html=True)
        if 'url_history' not in st.session_state:
            st.session_state.url_history = []

        if st.session_state.url_history:
            for idx, historic_url in enumerate(reversed(st.session_state.url_history[-5:])):
                if st.button(f"{historic_url[:40]}...", key=f"hist_{idx}", use_container_width=True):
                    st.session_state.selected_url = historic_url
                    st.rerun()
        else:
            st.info("No URLs processed yet")

        st.divider()

        # Help section
        st.markdown("""
            <div style="display: flex; align-items: center; margin: 1.5rem 0 0.5rem 0;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2" style="margin-right: 8px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                <h3 style="margin: 0; color: #e5e7eb; font-size: 0.9rem;">About</h3>
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

    # Main content area
    if not api_key:
        st.warning("Please provide a Groq API key in the sidebar or .env file")
        st.stop()

    # URL input with icon
    st.markdown("""
        <div style="display: flex; align-items: center; margin-top: 1.5rem; margin-bottom: 0.3rem;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2" style="margin-right: 6px;">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
            </svg>
            <span style="color: #9ca3af; font-size: 0.875rem;">Enter URL</span>
        </div>
    """, unsafe_allow_html=True)

    default_url = st.session_state.get('selected_url', '')
    url = st.text_input(
        "url_input",
        value=default_url,
        placeholder="https://example.com/dataset",
        label_visibility="collapsed"
    )

    # Example URLs section
    with st.expander("Need an example? Try these URLs"):
        st.markdown("**Government & Statistics:**")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("French Open Data", key="ex1", use_container_width=True):
                st.session_state.selected_url = "https://data.gouv.fr"
                st.rerun()
            if st.button("Norway Statistics", key="ex2", use_container_width=True):
                st.session_state.selected_url = "https://www.ssb.no"
                st.rerun()

        with col2:
            if st.button("Canada Statistics", key="ex3", use_container_width=True):
                st.session_state.selected_url = "https://www.statcan.gc.ca"
                st.rerun()
            if st.button("GitHub Repository", key="ex4", use_container_width=True):
                st.session_state.selected_url = "https://github.com/torvalds/linux"
                st.rerun()

    # Extract button - full width for professional appearance
    extract_button = st.button("Extract Metadata", type="primary", use_container_width=True)

    if extract_button:
        if not url:
            st.warning("Please enter a URL to analyze")
            return

        # Add to history
        if url not in st.session_state.url_history:
            st.session_state.url_history.append(url)

        try:
            # Initialize browser automation client with timeout
            client = GroqBrowserAutomation(api_key=api_key, model=model, timeout=timeout)

            # Try extraction with timeout handling and progress tracking
            import time
            start_time = time.time()

            # Create progress indicators
            progress_bar = st.progress(0)
            status_container = st.empty()

            # Step 1: Initialize
            status_container.info("Initializing browser automation (timeout: 4 minutes, max retries: 3)...")
            progress_bar.progress(0.15)
            time.sleep(0.3)

            # Step 2: Starting extraction
            status_container.info("Visiting main page and discovering links...")
            progress_bar.progress(0.30)

            # Actual extraction with automatic retry on failure
            attempt = 1
            result = client.extract_all_metadata(url, max_retries=max_retries)

            # If first attempt fails, automatically retry once more
            if not result.get("success") and attempt == 1:
                attempt += 1
                status_container.warning(f"Attempt {attempt-1} failed, retrying automatically (attempt {attempt}/2)...")
                progress_bar.progress(0.40)
                time.sleep(2)
                result = client.extract_all_metadata(url, max_retries=max_retries)

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

            if result.get("success"):
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
                            if st.button(f"⏱ Wait {wait_time:.0f}s and Retry", use_container_width=True, key="wait_retry"):
                                import time
                                with st.spinner(f"Waiting {wait_time:.0f} seconds..."):
                                    time.sleep(wait_time + 1)  # Add 1 second buffer
                                st.rerun()
                        with col2:
                            if st.button("🔄 Retry Now", use_container_width=True, key="retry_now"):
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
                        # Extract base URL
                        parts = url.split("/")
                        main_url = "/".join(parts[:3])  # https://www.ssb.no
                        st.markdown(f"""
                        1. **Try the main website instead:**
                        """)
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
                        st.info(f"""
                        **API Endpoint Detected:**
                        Your URL contains `/api/` which suggests it's a data endpoint, not a webpage.

                        Try this instead: `{main_url}`
                        """)

                # API endpoint errors
                elif "/api/" in url:
                    main_url = url.split("/api/")[0]
                    st.markdown(f"""
                    **API Endpoint Detected:**

                    Your URL appears to be an API endpoint (contains `/api/`).
                    Browser automation works best with regular web pages.

                    **Suggested URL:** `{main_url}`

                    Click the button below to try the main website:
                    """)
                    if st.button(f"Try {main_url}", use_container_width=True):
                        st.session_state.selected_url = main_url
                        st.rerun()

                # Connection errors
                elif "connection" in error_msg.lower():
                    st.markdown("""
                    **Connection Error:**

                    **What you can do:**
                    1. **Check your internet connection**
                    2. **Verify the URL is correct** - Make sure there are no typos
                    3. **Try a known working URL** - Use one of the examples above
                    """)

                # Authentication errors
                elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                    st.markdown("""
                    **API Key Issue:**

                    **What you can do:**
                    1. **Check your `.env` file** - Ensure `GROQ_API_KEY` is set correctly
                    2. **Restart the application** - Sometimes environment changes need a restart
                    3. **Verify your API key** - Make sure it's valid and active
                    """)

                # Generic errors
                else:
                    st.markdown("""
                    **Common Solutions:**
                    1. **Click Extract again** - Sometimes a retry works
                    2. **Wait 30 seconds** - The server might be rate limiting
                    3. **Try a different URL** - Test with one of the example URLs above
                    4. **Check the URL in browser** - Make sure it loads normally
                    """)

                    # Add retry button
                    if st.button("🔄 Retry Extraction", use_container_width=True):
                        st.rerun()

                # Always show technical details in expander with full trace
                with st.expander("Show full technical error details"):
                    st.code(error_msg)

                    # Show result object for debugging
                    st.json({
                        "success": result.get("success"),
                        "error": result.get("error"),
                        "content": result.get("content", "None")[:200] if result.get("content") else "None",
                        "reasoning": result.get("reasoning", "None")[:200] if result.get("reasoning") else "None",
                        "executed_tools": len(result.get("executed_tools", [])),
                    })

        except TimeoutError:
            st.error("Request Timed Out")
            st.markdown("""
            **The extraction exceeded the time limit.**

            **What you can do:**
            1. **Try the main website URL** - Avoid specific page or API endpoints
            2. **Use one of the example URLs** - These are known to work well
            3. **Try again** - The site may be temporarily slow
            """)

        except Exception as e:
            st.error("An Unexpected Error Occurred")
            st.markdown("""
            **What you can do:**
            1. **Verify your API key** - Check the `.env` file
            2. **Check your internet connection**
            3. **Try a simpler URL** - Test with an example URL first
            """)
            with st.expander("Show technical error details"):
                st.exception(e)

    # Footer
    st.divider()
    st.caption("Powered by Groq Browser Automation")


if __name__ == "__main__":
    main()
