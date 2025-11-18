"""Test script for browser automation implementation."""
import os
from dotenv import load_dotenv
from src.utils.groq_browser_automation import GroqBrowserAutomation


def test_initialization():
    """Test client initialization."""
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')

    if not api_key:
        print("❌ Error: GROQ_API_KEY not found in .env")
        return False

    print("✅ API key loaded successfully")

    # Test with default model
    try:
        client = GroqBrowserAutomation(api_key=api_key)
        print(f"✅ Client initialized with default model: {client.model}")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False

    # Test with different models
    models = [
        "moonshotai/kimi-k2-instruct-0905",
        "groq/compound-mini",
        "groq/compound"
    ]

    for model in models:
        try:
            client = GroqBrowserAutomation(api_key=api_key, model=model)
            print(f"✅ Client initialized with model: {model}")
        except Exception as e:
            print(f"❌ Failed to initialize with {model}: {e}")

    return True


def test_import():
    """Test that all imports work correctly."""
    try:
        from src.utils.groq_browser_automation import GroqBrowserAutomation
        print("✅ GroqBrowserAutomation import successful")

        from src.orchestrator import MetadataOrchestrator
        print("✅ MetadataOrchestrator import successful")

        from src.utils.groq_browser_client import GroqBrowserClient
        print("✅ GroqBrowserClient import successful")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 80)
    print("  Browser Automation Implementation Test")
    print("=" * 80)
    print()

    print("Test 1: Checking imports...")
    print("-" * 80)
    import_ok = test_import()
    print()

    print("Test 2: Testing client initialization...")
    print("-" * 80)
    init_ok = test_initialization()
    print()

    print("=" * 80)
    if import_ok and init_ok:
        print("✅ All tests passed!")
        print()
        print("You can now use the browser automation extractor:")
        print("  python browser_automation_extractor.py <url>")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 80)


if __name__ == "__main__":
    main()
