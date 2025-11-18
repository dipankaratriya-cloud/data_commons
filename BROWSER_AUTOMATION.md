# Browser Automation - Advanced Metadata Extraction

This project now includes Groq's advanced browser automation capabilities, enabling simultaneous control of up to 10 browsers for comprehensive metadata extraction.

## Overview

The browser automation feature uses Groq's Compound system with the `moonshotai/kimi-k2-instruct-0905` model to launch multiple browsers simultaneously, gathering information from various sources for deeper and more accurate metadata extraction.

## Features

- **Parallel Browser Control**: Launch up to 10 browsers simultaneously
- **Deep Web Research**: Navigate through multiple pages and documentation
- **Comprehensive Analysis**: Gather evidence from multiple sources
- **Intelligent Reasoning**: See how the system navigates and makes decisions
- **Multiple Extraction Modes**: License, Place, Temporal, or All metadata at once

## Quick Start

### Basic Usage

```bash
# Extract all metadata types
python browser_automation_extractor.py https://example.com/dataset

# Extract only license information
python browser_automation_extractor.py https://example.com/dataset --mode=license

# Extract place information
python browser_automation_extractor.py https://example.com/dataset --mode=place

# Extract temporal information
python browser_automation_extractor.py https://example.com/dataset --mode=temporal
```

### Advanced Options

```bash
# Use the full Compound model (more thorough but slower)
python browser_automation_extractor.py https://example.com/dataset --model=groq/compound

# Save to specific output file
python browser_automation_extractor.py https://example.com/dataset --output=results.json

# Don't save results to file
python browser_automation_extractor.py https://example.com/dataset --no-save
```

## Models Available

### Default: moonshotai/kimi-k2-instruct-0905
- Fast and efficient
- Good for most use cases
- Recommended for production

### Alternative: groq/compound-mini
- Lightweight version of Compound
- Good balance of speed and depth
- Cost-effective

### Alternative: groq/compound
- Most thorough research
- Multiple browser sessions
- Best for complex datasets
- Higher cost but more comprehensive

## How It Works

1. **Query Construction**: Based on your mode (license, place, temporal, all), the system constructs an optimized query
2. **Browser Launch**: Multiple browsers are launched simultaneously to search different sources
3. **Parallel Navigation**: Each browser independently navigates and extracts information
4. **Evidence Gathering**: Information from all browser sessions is collected
5. **Synthesis**: The model combines findings into a comprehensive response
6. **Structured Output**: Results are formatted and optionally saved to JSON

## Output Structure

The system provides three key components in its output:

### 1. Content
The final synthesized response with extracted metadata:
- License information (type, URL, requirements)
- Place/geographic coverage details
- Temporal coverage and update frequency
- Confidence levels and data quality indicators

### 2. Reasoning
The internal decision-making process showing:
- Which browsers were launched
- What sources were accessed
- How information was prioritized
- Navigation decisions made

### 3. Executed Tools
Detailed information about:
- Browser automation sessions
- Web searches performed
- Pages visited
- Content analyzed

## Python API Usage

```python
from src.utils.groq_browser_automation import GroqBrowserAutomation

# Initialize client
client = GroqBrowserAutomation(
    api_key="your-groq-api-key",
    model="moonshotai/kimi-k2-instruct-0905"  # or groq/compound, groq/compound-mini
)

# Extract all metadata
result = client.extract_all_metadata("https://example.com/dataset")

# Access results
if result["success"]:
    print("Content:", result["content"])
    print("Reasoning:", result["reasoning"])
    print("Browser Sessions:", len(result["executed_tools"]))

# Extract specific metadata types
license_result = client.extract_license_metadata(url)
place_result = client.extract_place_metadata(url)
temporal_result = client.extract_temporal_metadata(url)
```

## Example Output

When you run the extractor, you'll see:

```
================================================================================
  🤖 Groq Browser Automation - Metadata Extractor
================================================================================

📎 URL: https://example.com/dataset
📋 Mode: all
🤖 Model: moonshotai/kimi-k2-instruct-0905

🔧 Initializing browser automation client...
🌐 Launching browsers for all extraction...
⏳ This may take a moment as multiple browsers gather information...

================================================================================
  COMPREHENSIVE METADATA EXTRACTION
================================================================================

📋 Complete Metadata Analysis:
--------------------------------------------------------------------------------
[Detailed metadata extracted from multiple sources]

🧠 Browser Automation Process:
--------------------------------------------------------------------------------
[Shows how browsers navigated and made decisions]

🔧 Browser Sessions Summary:
--------------------------------------------------------------------------------
Total browser sessions: 5
  Session 1: browser_automation
  Session 2: web_search
  [...]

💾 Results saved to: metadata_extraction_example_com_20250118_142035.json

================================================================================
  EXTRACTION COMPLETE
================================================================================
✅ Metadata extraction completed successfully!

💡 Tips:
  - Use --model=groq/compound for more thorough research
  - Check the reasoning section to see how browsers navigated
  - Multiple browser sessions mean more comprehensive results
```

## Comparison with Standard Extraction

| Feature | Standard Extraction | Browser Automation |
|---------|-------------------|-------------------|
| Speed | Faster | Slower but thorough |
| Depth | Single page | Multiple pages |
| Accuracy | Good | Excellent |
| Sources | Limited | Multiple simultaneous |
| Cost | Lower | Higher |
| Best For | Quick checks | Comprehensive analysis |

## Use Cases

### When to Use Browser Automation

✅ **Use when:**
- You need comprehensive, high-confidence metadata
- Dataset documentation is spread across multiple pages
- You want to verify information from multiple sources
- Quality is more important than speed
- You need detailed reasoning about findings

❌ **Standard extraction is better when:**
- You need quick results
- Budget is a primary concern
- Dataset has simple, single-page metadata
- You're processing many datasets in batch

## Configuration

### Environment Variables

```bash
# In your .env file
GROQ_API_KEY=your-api-key-here
LLM_MODEL=moonshotai/kimi-k2-instruct-0905
```

### Custom Prompts

You can customize the extraction prompts by modifying the methods in `src/utils/groq_browser_automation.py`:

- `extract_license_metadata()` - License extraction prompt
- `extract_place_metadata()` - Place/geographic prompt
- `extract_temporal_metadata()` - Temporal coverage prompt
- `extract_all_metadata()` - Combined extraction prompt

## Troubleshooting

### "Browser automation not supported"
- Make sure you're using a supported model (moonshotai/kimi-k2-instruct-0905, groq/compound, or groq/compound-mini)
- Verify your API key has access to browser automation features

### "No results returned"
- Check if the URL is publicly accessible
- Try with a different mode (--mode=license instead of --mode=all)
- Verify your internet connection

### Slow performance
- Switch to groq/compound-mini for faster results
- Use specific modes (--mode=license) instead of --mode=all
- Check your API rate limits

## Cost Considerations

Browser automation uses more API resources than standard extraction:

- **moonshotai/kimi-k2-instruct-0905**: Most cost-effective for browser automation
- **groq/compound-mini**: Moderate cost, good balance
- **groq/compound**: Highest cost but most comprehensive

For batch processing, consider:
1. Using standard extraction first
2. Using browser automation only for datasets that need it
3. Caching results to avoid re-processing

## Integration with Existing Tools

The browser automation extractor works alongside existing extractors:

```python
from src.orchestrator import MetadataOrchestrator
from src.utils.groq_browser_automation import GroqBrowserAutomation

# Standard extraction
standard = MetadataOrchestrator(api_key)
quick_results = standard.extract_metadata(url)

# Browser automation (when you need more depth)
browser = GroqBrowserAutomation(api_key)
deep_results = browser.extract_all_metadata(url)

# Compare results
print("Standard confidence:", quick_results['validation']['overall_score'])
print("Browser automation sessions:", len(deep_results['executed_tools']))
```

## Future Enhancements

Planned improvements:
- Automatic fallback from standard to browser automation on low confidence
- Result caching and comparison
- Parallel processing of multiple URLs
- Custom browser navigation strategies
- Integration with Streamlit UI

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation: https://console.groq.com/docs/browser-automation
3. Check Groq's pricing page: https://groq.com/pricing
4. Review the example outputs in the project

## License

This feature uses Groq's browser automation API. Review Groq's terms of service for usage limits and restrictions.
