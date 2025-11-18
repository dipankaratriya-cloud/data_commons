"""Minimal Streamlit app for metadata extraction."""
import streamlit as st
import os
from dotenv import load_dotenv
from src.orchestrator import MetadataOrchestrator

# Load environment variables
load_dotenv()

# Initialize session state for history
if 'url_history' not in st.session_state:
    st.session_state.url_history = []


def format_license_output(license_data):
    """Format license information with clickable links."""
    if not license_data:
        return "No license information found."

    # Handle both dict and direct access
    if isinstance(license_data, dict):
        best = license_data.get('best_match', license_data)
    else:
        best = license_data

    # Return just the URL
    if best and best.get('license_url') and best['license_url'] not in ['null', None, '']:
        return best['license_url']

    return "No license information found."


def format_place_output(place_data):
    """Format place information - clean output."""
    if not place_data:
        return "No place information found."

    lines = []

    # Place types - simple list
    if place_data.get('place_types'):
        for place_type in place_data['place_types']:
            lines.append(place_type)

    return "\n".join(lines) if lines else "No place information found."


def format_place_id_resolution(place_data):
    """Format place ID resolution method."""
    if not place_data:
        return "No place ID resolution found."

    id_sys = place_data.get('place_id_systems', {})
    if id_sys.get('resolution_method'):
        return id_sys['resolution_method']

    return "No place ID resolution found."


def format_temporal_output(temporal_data):
    """Format temporal information - clean output."""
    if not temporal_data:
        return "No temporal information found."

    coverage = temporal_data.get('coverage_period', {})
    start = coverage.get('start_date', '')
    end = coverage.get('end_date', '')

    if start and end:
        return f"{start} - {end}"
    elif start:
        return start
    elif end:
        return end

    return "No temporal information found."


def main():
    st.set_page_config(
        page_title="Metadata Extractor",
        layout="centered"
    )

    # Get API key from environment
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        st.error("GROQ_API_KEY not found in .env file")
        st.stop()

    # Sidebar with URL history
    with st.sidebar:
        st.header("URL History")
        if st.session_state.url_history:
            for idx, historic_url in enumerate(reversed(st.session_state.url_history[-10:])):
                if st.button(f"🔗 {historic_url[:30]}...", key=f"hist_{idx}"):
                    st.session_state.current_url = historic_url
        else:
            st.info("No URLs processed yet")

    # Main content
    st.title("Metadata Extractor")

    # URL input
    default_url = st.session_state.get('current_url', '')
    url = st.text_input("URL", value=default_url, placeholder="https://example.com")

    if st.button("Extract Metadata", use_container_width=True):
        if not url:
            st.warning("Please enter a URL")
            return

        # Add to history
        if url not in st.session_state.url_history:
            st.session_state.url_history.append(url)

        try:
            with st.spinner("Extracting..."):
                orchestrator = MetadataOrchestrator(api_key)
                results = orchestrator.extract_metadata(
                    url,
                    extract_license=True,
                    extract_place=True,
                    extract_temporal=True
                )

            st.success("Extraction completed!")

            # Clean, simple output format
            st.markdown("---")

            # Place types covered
            if results.get('place'):
                st.markdown("**Place types covered**")
                st.text(format_place_output(results['place']))
                st.markdown("")

            # Place ID resolution
            if results.get('place'):
                st.markdown("**Place ID resolution**")
                st.text(format_place_id_resolution(results['place']))
                st.markdown("")

            # Date range covered
            if results.get('temporal'):
                st.markdown("**Date range covered**")
                st.text(format_temporal_output(results['temporal']))
                st.markdown("")

            # License
            if results.get('license'):
                st.markdown("**License**")
                st.text(format_license_output(results['license']))
                st.markdown("")

            # Errors
            if results.get('errors'):
                st.error("Errors occurred:")
                for error in results['errors']:
                    st.error(f"- {error}")

        except Exception as e:
            st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
