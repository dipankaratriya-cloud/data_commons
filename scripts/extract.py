#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to sys.path to allow importing src
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.groq_browser_automation import GroqBrowserAutomation

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

def main():
    parser = argparse.ArgumentParser(description='Extract metadata from URL using GroqBrowserAutomation')
    parser.add_argument('--url', required=True, help='URL to analyze')
    args = parser.parse_args()

    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print(json.dumps({"success": False, "error": "GROQ_API_KEY not found"}))
        sys.exit(1)

    try:
        client = GroqBrowserAutomation(
            api_key=api_key,
            model="groq/compound",
            timeout=240
        )
        
        result = client.extract_all_metadata(args.url, max_retries=3)
        
        # Convert executed_tools to serializable format if needed
        if result.get("executed_tools"):
            serializable_tools = []
            for tool in result["executed_tools"]:
                if hasattr(tool, '__dict__'):
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
            result["executed_tools"] = serializable_tools

        print(json.dumps(result, default=str))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
