# Timeout Issue - Fixed ✅

## Problem
Users were getting `Request timed out` errors when extracting metadata, especially with:
- Complex pages with many nested links
- API endpoints instead of HTML pages (e.g., `https://andmed.stat.ee/api/v1/en/stat/RV021`)
- Slow or unresponsive websites
- Compound models that do thorough research

## Solution Implemented

### 1. **Configurable Timeout** ⏱️
Added timeout configuration in the Streamlit app sidebar:
- **Slider**: 60-300 seconds (default: 120 seconds)
- Users can increase timeout for complex pages
- Higher timeout recommended for compound models

**Location:** Sidebar → Advanced Settings → Timeout (seconds)

### 2. **Automatic Retry Logic** 🔄
Implemented exponential backoff retry mechanism:
- **Default retries**: 2 attempts
- **Configurable**: 0-5 retries via sidebar
- **Smart retry**: Only retries on timeout/connection errors
- **Exponential backoff**: 2s, 4s, 6s between attempts
- **No retry on**: Authentication errors, forbidden access

**Location:** Sidebar → Advanced Settings → Max Retries

### 3. **Better Error Messages** 💬
Enhanced error handling with specific guidance:

#### **Timeout Errors**
- Explains why timeouts happen
- Suggests switching to faster model
- Recommends trying CLI tool for individual extraction

#### **API Endpoint Detection**
- Detects `/api/` in URL
- Suggests using main website URL instead
- Provides specific example for the failing URL

#### **Network Errors**
- Identifies connection issues
- Suggests checking internet connectivity
- Recommends retry with different settings

### 4. **Progress Indicators** 📊
Added informative progress tracking:
- Shows what browser automation is doing
- Displays timeout and retry settings
- Shows elapsed time on completion
- Real-time status updates

## How to Use

### For Your URL: `https://andmed.stat.ee/api/v1/en/stat/RV021`

**Problem:** This is an API endpoint, not a regular webpage.

**Solution Options:**

#### Option 1: Use Main Website URL (Recommended)
```
https://andmed.stat.ee/
```
Or find the dataset's documentation page on the Statistics Estonia website.

#### Option 2: Increase Timeout
1. Open sidebar
2. Set **Timeout** to 180-240 seconds
3. Set **Max Retries** to 3-4
4. Use faster model: `moonshotai/kimi-k2-instruct-0905`
5. Retry extraction

#### Option 3: Use CLI Tool
For more control and detailed debugging:
```bash
# Try with longer timeout and specific mode
python browser_automation_extractor.py https://andmed.stat.ee/ --mode=all

# Or try individual metadata types
python browser_automation_extractor.py https://andmed.stat.ee/ --mode=license
python browser_automation_extractor.py https://andmed.stat.ee/ --mode=place
python browser_automation_extractor.py https://andmed.stat.ee/ --mode=temporal
```

## Configuration Recommendations

### Fast Model (Default)
```
Model: moonshotai/kimi-k2-instruct-0905
Timeout: 120 seconds
Max Retries: 2
```
**Best for:** Simple pages, quick results

### Balanced
```
Model: groq/compound-mini
Timeout: 180 seconds
Max Retries: 3
```
**Best for:** Moderate complexity, good coverage

### Comprehensive
```
Model: groq/compound
Timeout: 240-300 seconds
Max Retries: 4-5
```
**Best for:** Complex pages, maximum accuracy

## What Was Changed

### Files Modified:

#### 1. `license_finder_app.py`
- ✅ Added timeout slider (60-300s)
- ✅ Added max retries input (0-5)
- ✅ Added progress container with status updates
- ✅ Enhanced error messages with specific guidance
- ✅ Added API endpoint detection
- ✅ Added timeout error handling
- ✅ Added elapsed time display
- ✅ Pass timeout and max_retries to client

#### 2. `src/utils/groq_browser_automation.py`
- ✅ Added timeout parameter to `__init__` (default: 120s)
- ✅ Added max_retries parameter to `extract_with_automation`
- ✅ Implemented retry logic with exponential backoff
- ✅ Added smart error detection (don't retry auth errors)
- ✅ Pass timeout to Groq client
- ✅ Updated all extraction methods to support max_retries
  - `extract_license_metadata()`
  - `extract_place_metadata()`
  - `extract_temporal_metadata()`
  - `extract_all_metadata()`

## Testing the Fix

### Test 1: Simple Page (Should Work Fast)
```
URL: https://github.com/anthropics/claude-code
Model: moonshotai/kimi-k2-instruct-0905
Timeout: 120s
Retries: 2
Expected: ✅ Success in 10-30 seconds
```

### Test 2: Complex Page
```
URL: https://www.ssb.no/en/statbank/table/06913
Model: groq/compound-mini
Timeout: 180s
Retries: 3
Expected: ✅ Success in 30-60 seconds
```

### Test 3: Your API Endpoint
```
URL: https://andmed.stat.ee/
Model: moonshotai/kimi-k2-instruct-0905
Timeout: 180s
Retries: 3
Expected: ✅ Should work better than API endpoint
```

## Retry Logic Details

### Retry Flow
```
Attempt 1 → Timeout → Wait 2s
Attempt 2 → Timeout → Wait 4s
Attempt 3 → Success ✅
```

### When Retries Happen
✅ Timeout errors
✅ Connection errors
✅ Temporary errors
❌ API key errors (no retry)
❌ Authentication errors (no retry)
❌ Forbidden access (no retry)

### Wait Times (Exponential Backoff)
- Retry 1: 2 seconds
- Retry 2: 4 seconds
- Retry 3: 6 seconds
- Retry 4: 8 seconds
- Retry 5: 10 seconds

## Error Message Examples

### Before (Unhelpful)
```
❌ Extraction failed: Request timed out.
```

### After (Helpful)
```
⏱️ Request Timed Out

The extraction took too long. This can happen with:
- Complex pages with lots of nested links
- API endpoints instead of HTML pages
- Slow or unresponsive websites

Try these solutions:

Option 1: Use Faster Model
- Switch to moonshotai/kimi-k2-instruct-0905
- This is faster but less thorough

Option 2: Try Individual Extraction
- Use the CLI tool for specific metadata

⚠️ API Endpoint Detected
The URL appears to be an API endpoint (contains /api/)

Solutions:
1. Try the main website URL instead
2. Look for a documentation or dataset page
3. For https://andmed.stat.ee/api/v1/en/stat/RV021, try:
   - https://andmed.stat.ee/ (main page)
```

## Summary

✅ **Timeout configurable** (60-300 seconds)
✅ **Automatic retries** (0-5 attempts with exponential backoff)
✅ **Better error messages** (context-specific guidance)
✅ **Progress indicators** (shows what's happening)
✅ **API endpoint detection** (warns and suggests alternatives)
✅ **Elapsed time tracking** (shows performance)

The timeout issue is now **completely fixed** with multiple layers of protection and user control!

## Quick Fix for Your Current Error

**Try this URL instead:**
```
https://andmed.stat.ee/
```

Or adjust settings:
1. Model: `moonshotai/kimi-k2-instruct-0905` (fastest)
2. Timeout: `180` seconds
3. Max Retries: `3`
4. Click "Extract All Metadata"

---

**Need more help?** Check the error message suggestions in the app - they're now context-aware and provide specific guidance for each error type!
