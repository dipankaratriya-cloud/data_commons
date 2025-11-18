#!/usr/bin/env python3
"""Browser Automation Metadata Extractor - CLI Tool

This script uses Groq's browser automation capabilities to extract
comprehensive metadata from dataset URLs. It can launch and control
up to 10 browsers simultaneously for deep web research.

Usage:
    python browser_automation_extractor.py <url>
    python browser_automation_extractor.py <url> --mode=all
    python browser_automation_extractor.py <url> --mode=license
    python browser_automation_extractor.py <url> --model=groq/compound
"""

import argparse
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from src.utils.groq_browser_automation import GroqBrowserAutomation


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def print_section(title):
    """Print a section title."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def format_license_output(result: dict):
    """Format and display license extraction results."""
    print_section("LICENSE INFORMATION")

    if not result.get("success"):
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return

    # Display main content
    print("📄 Extracted License Information:")
    print("-" * 80)
    print(result["content"])
    print()

    # Display parsed data if available
    if result.get("license_data"):
        print("\n📊 Structured Data:")
        print("-" * 80)
        license_data = result["license_data"]
        if license_data.get("license_type"):
            print(f"License Type: {license_data['license_type']}")
        if license_data.get("license_url"):
            print(f"License URL: {license_data['license_url']}")
        if license_data.get("confidence"):
            print(f"Confidence: {license_data['confidence']}")
        print()

    # Display reasoning if available
    if result.get("reasoning"):
        print("\n🧠 Browser Automation Reasoning:")
        print("-" * 80)
        print(result["reasoning"][:500])  # First 500 chars
        if len(result["reasoning"]) > 500:
            print("... (truncated)")
        print()

    # Display executed tools
    if result.get("executed_tools"):
        print("\n🔧 Browser Automation Sessions:")
        print("-" * 80)
        for i, tool in enumerate(result["executed_tools"], 1):
            print(f"\nSession {i}:")
            print(f"  Type: {tool.get('type', 'unknown')}")
            if tool.get('output'):
                output_preview = tool['output'][:200]
                print(f"  Output: {output_preview}...")
        print()


def format_place_output(result: dict):
    """Format and display place extraction results."""
    print_section("GEOGRAPHIC/PLACE INFORMATION")

    if not result.get("success"):
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return

    print("🌍 Extracted Geographic Coverage:")
    print("-" * 80)
    print(result["content"])
    print()


def format_temporal_output(result: dict):
    """Format and display temporal extraction results."""
    print_section("TEMPORAL INFORMATION")

    if not result.get("success"):
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return

    print("📅 Extracted Temporal Coverage:")
    print("-" * 80)
    print(result["content"])
    print()


def format_all_metadata(result: dict):
    """Format and display all metadata extraction results."""
    print_section("COMPREHENSIVE METADATA EXTRACTION")

    if not result.get("success"):
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return

    print("📋 Complete Metadata Analysis:")
    print("-" * 80)
    print(result["content"])
    print()

    # Display reasoning
    if result.get("reasoning"):
        print("\n🧠 Browser Automation Process:")
        print("-" * 80)
        reasoning_lines = result["reasoning"].split('\n')
        for line in reasoning_lines[:20]:  # First 20 lines
            print(line)
        if len(reasoning_lines) > 20:
            print(f"... ({len(reasoning_lines) - 20} more lines)")
        print()

    # Display tool execution summary
    if result.get("executed_tools"):
        print("\n🔧 Browser Sessions Summary:")
        print("-" * 80)
        print(f"Total browser sessions: {len(result['executed_tools'])}")
        for i, tool in enumerate(result["executed_tools"], 1):
            print(f"  Session {i}: {tool.get('type', 'unknown')}")
        print()


def save_results(result: dict, url: str, mode: str, output_file: str = None):
    """Save results to a JSON file."""
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_url = url.replace("https://", "").replace("http://", "").replace("/", "_")[:50]
        output_file = f"metadata_extraction_{safe_url}_{timestamp}.json"

    # Create a copy without non-serializable objects
    result_copy = {
        "success": result.get("success"),
        "content": result.get("content"),
        "reasoning": result.get("reasoning"),
        "executed_tools": result.get("executed_tools"),
        "error": result.get("error"),
        "license_data": result.get("license_data"),
        "place_data": result.get("place_data"),
        "temporal_data": result.get("temporal_data"),
        "parsed_metadata": result.get("parsed_metadata")
    }

    output_data = {
        "url": url,
        "mode": mode,
        "timestamp": datetime.now().isoformat(),
        "result": result_copy
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n💾 Results saved to: {output_file}")


def main():
    """Main CLI function."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Extract metadata using Groq Browser Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all metadata types
  python browser_automation_extractor.py https://example.com/dataset

  # Extract only license information
  python browser_automation_extractor.py https://example.com/dataset --mode=license

  # Extract place information with full model
  python browser_automation_extractor.py https://example.com/dataset --mode=place --model=groq/compound

  # Save results to specific file
  python browser_automation_extractor.py https://example.com/dataset --output=results.json
        """
    )

    parser.add_argument(
        "url",
        help="Dataset URL to extract metadata from"
    )

    parser.add_argument(
        "--mode",
        choices=["all", "license", "place", "temporal"],
        default="all",
        help="Type of metadata to extract (default: all)"
    )

    parser.add_argument(
        "--model",
        choices=["moonshotai/kimi-k2-instruct-0905", "groq/compound-mini", "groq/compound"],
        default="moonshotai/kimi-k2-instruct-0905",
        help="Model to use for extraction (default: moonshotai/kimi-k2-instruct-0905)"
    )

    parser.add_argument(
        "--output",
        help="Output JSON file path (auto-generated if not specified)"
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to file"
    )

    args = parser.parse_args()

    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ Error: GROQ_API_KEY not found in environment variables")
        print("Please set your API key in .env file or environment")
        sys.exit(1)

    # Display header
    print_separator("=")
    print("  🤖 Groq Browser Automation - Metadata Extractor")
    print_separator("=")
    print(f"\n📎 URL: {args.url}")
    print(f"📋 Mode: {args.mode}")
    print(f"🤖 Model: {args.model}")
    print()

    # Initialize client
    print("🔧 Initializing browser automation client...")
    client = GroqBrowserAutomation(api_key=api_key, model=args.model)

    # Extract metadata based on mode
    print(f"🌐 Launching browsers for {args.mode} extraction...")
    print("⏳ This may take a moment as multiple browsers gather information...\n")

    try:
        if args.mode == "license":
            result = client.extract_license_metadata(args.url)
            format_license_output(result)
        elif args.mode == "place":
            result = client.extract_place_metadata(args.url)
            format_place_output(result)
        elif args.mode == "temporal":
            result = client.extract_temporal_metadata(args.url)
            format_temporal_output(result)
        else:  # all
            result = client.extract_all_metadata(args.url)
            format_all_metadata(result)

        # Save results
        if not args.no_save:
            save_results(result, args.url, args.mode, args.output)

        # Display summary
        print_section("EXTRACTION COMPLETE")
        print("✅ Metadata extraction completed successfully!")
        print()
        print("💡 Tips:")
        print("  - Use --model=groq/compound for more thorough research")
        print("  - Check the reasoning section to see how browsers navigated")
        print("  - Multiple browser sessions mean more comprehensive results")
        print()

    except Exception as e:
        print(f"\n❌ Error during extraction: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
