#!/usr/bin/env python3
"""Streamlit app for finding license information using Browser Automation.

This app uses Groq's browser automation capabilities to search through
web pages and nested links to find license information.
"""

import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from src.utils.groq_browser_automation import GroqBrowserAutomation

# Load environment variables
load_dotenv()


def format_license_display(result: dict):
    """Format and display license extraction results in Streamlit."""
    if not result.get("success"):
        st.error(f"Error: {result.get('error', 'Unknown error')}")
        return

    # Display main content
    st.subheader("📄 License Information Found")
    with st.expander("View Full License Details", expanded=True):
        st.markdown(result["content"])

    # Display structured data if available
    if result.get("license_data"):
        st.subheader("📊 Structured License Data")
        license_data = result["license_data"]

        col1, col2 = st.columns(2)

        with col1:
            if license_data.get("license_type"):
                st.metric("License Type", license_data["license_type"])
            if license_data.get("confidence"):
                confidence = license_data["confidence"]
                emoji = "🟢" if confidence == "high" else "🟡" if confidence == "medium" else "🔴"
                st.metric("Confidence", f"{emoji} {confidence.capitalize()}")

        with col2:
            if license_data.get("license_url"):
                st.markdown("**License URL:**")
                st.markdown(f"[Open License Page]({license_data['license_url']})")

    # Display browser automation details
    if result.get("executed_tools"):
        st.subheader("🔧 Browser Automation Sessions")
        st.info(f"Launched {len(result['executed_tools'])} browser session(s) to gather information")

        with st.expander("View Browser Session Details"):
            for i, tool in enumerate(result["executed_tools"], 1):
                st.markdown(f"**Session {i}:**")
                st.text(f"Type: {tool.get('type', 'unknown')}")
                if tool.get('output'):
                    output_preview = tool['output'][:300]
                    st.text_area(f"Output Preview (Session {i})", output_preview, height=100)
                st.divider()

    # Display reasoning if available
    if result.get("reasoning"):
        with st.expander("🧠 How the Browser Automation Worked"):
            st.text_area("Decision-Making Process", result["reasoning"], height=200)


def save_results_json(result: dict, url: str):
    """Save results to JSON file and provide download button."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_url = url.replace("https://", "").replace("http://", "").replace("/", "_")[:50]
    filename = f"license_extraction_{safe_url}_{timestamp}.json"

    output_data = {
        "url": url,
        "extraction_type": "license",
        "timestamp": datetime.now().isoformat(),
        "result": {
            "success": result.get("success"),
            "content": result.get("content"),
            "license_data": result.get("license_data"),
            "reasoning": result.get("reasoning"),
            "executed_tools": result.get("executed_tools"),
            "error": result.get("error")
        }
    }

    json_str = json.dumps(output_data, indent=2, ensure_ascii=False, default=str)

    st.download_button(
        label="💾 Download Results as JSON",
        data=json_str,
        file_name=filename,
        mime="application/json",
        use_container_width=True
    )


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="License Finder - Browser Automation",
        page_icon="📜",
        layout="wide"
    )

    # Header
    st.title("📜 License Finder with Browser Automation")
    st.markdown("""
    This tool uses Groq's browser automation to search through web pages and nested links
    to find license information. It can launch multiple browsers to thoroughly research
    license details across different pages.
    """)

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            api_key = st.text_input(
                "Groq API Key",
                type="password",
                help="Enter your Groq API key or set GROQ_API_KEY in .env file"
            )
        else:
            st.success("✅ API Key loaded from environment")

        # Model selection
        model = st.selectbox(
            "Model",
            [
                "moonshotai/kimi-k2-instruct-0905",
                "groq/compound-mini",
                "groq/compound"
            ],
            help="Choose the model for browser automation. 'compound' models provide more thorough research."
        )

        st.divider()

        # URL History
        st.header("📚 Recent URLs")
        if 'url_history' not in st.session_state:
            st.session_state.url_history = []

        if st.session_state.url_history:
            for idx, historic_url in enumerate(reversed(st.session_state.url_history[-5:])):
                if st.button(f"🔗 {historic_url[:35]}...", key=f"hist_{idx}", use_container_width=True):
                    st.session_state.selected_url = historic_url
                    st.rerun()
        else:
            st.info("No URLs processed yet")

        st.divider()

        # Help section
        with st.expander("ℹ️ How it works"):
            st.markdown("""
            **Browser Automation Process:**
            1. Launches browsers to visit the URL
            2. Searches for license links and pages
            3. Navigates through nested pages
            4. Extracts and validates license info
            5. Returns structured results

            **What it finds:**
            - License type (CC-BY, MIT, etc.)
            - License URLs
            - Attribution requirements
            - Usage restrictions
            - Confidence level
            """)

    # Main content area
    if not api_key:
        st.warning("⚠️ Please provide a Groq API key in the sidebar or .env file")
        st.stop()

    # URL input
    default_url = st.session_state.get('selected_url', '')
    url = st.text_input(
        "🌐 Enter URL to analyze",
        value=default_url,
        placeholder="https://example.com/dataset",
        help="Enter the URL of the webpage where you want to find license information"
    )

    # Extract button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        extract_button = st.button("🚀 Find License Information", type="primary", use_container_width=True)

    if extract_button:
        if not url:
            st.warning("⚠️ Please enter a URL to analyze")
            return

        # Add to history
        if url not in st.session_state.url_history:
            st.session_state.url_history.append(url)

        # Display extraction info
        st.info(f"🌐 Analyzing: {url}")
        st.info(f"🤖 Using model: {model}")

        try:
            with st.spinner("🔄 Launching browsers and searching for license information... This may take a moment."):
                # Initialize browser automation client
                client = GroqBrowserAutomation(api_key=api_key, model=model)

                # Extract license metadata
                result = client.extract_license_metadata(url)

            # Display results
            st.divider()

            if result.get("success"):
                st.success("✅ License extraction completed successfully!")
                format_license_display(result)

                # Download button
                st.divider()
                save_results_json(result, url)

            else:
                st.error(f"❌ Extraction failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.exception(e)

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
    <small>Powered by Groq Browser Automation | Built with Streamlit</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
