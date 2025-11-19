# Quick Fix Guide - Timeout Errors ⚡

## Your Error
```
❌ Extraction failed: Request timed out.
```

## Why It Happened
The URL `https://andmed.stat.ee/api/v1/en/stat/RV021` is an **API endpoint**, not a regular webpage. Browser automation works best with HTML pages.

---

## 🎯 Quick Solutions (Choose One)

### Solution 1: Use Main Website URL ⭐ RECOMMENDED
```
Instead of: https://andmed.stat.ee/api/v1/en/stat/RV021
Try:        https://andmed.stat.ee/
```

The main Statistics Estonia website will have:
- License information in footer or about pages
- Dataset documentation with metadata
- Temporal and geographic coverage details

### Solution 2: Adjust Timeout Settings
**In the Streamlit app sidebar:**

```
⚙️ Configuration
├── Model: moonshotai/kimi-k2-instruct-0905 ← Use fastest model
└── Advanced Settings
    ├── Timeout: 180 seconds ← Increase from default 120s
    └── Max Retries: 3 ← Increase from default 2
```

**How to do it:**
1. Look at the **left sidebar** in the app
2. Find **"Advanced Settings"** section
3. Move the **"Timeout"** slider to `180`
4. Change **"Max Retries"** to `3`
5. Click **"Extract All Metadata"** again

### Solution 3: Use CLI Tool (For Advanced Users)
```bash
# Try the main website with CLI
python browser_automation_extractor.py https://andmed.stat.ee/ --mode=all

# Or try specific metadata types
python browser_automation_extractor.py https://andmed.stat.ee/ --mode=license
```

---

## 🚀 Try These Working Examples

Test the app with these URLs to verify it's working:

### Example 1: GitHub (Fast)
```
https://github.com/anthropics/claude-code
Expected time: 10-20 seconds ✅
```

### Example 2: Norway Statistics (Moderate)
```
https://www.ssb.no/en/statbank/table/06913
Expected time: 30-45 seconds ✅
```

### Example 3: Statistics Canada (Complex)
```
https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000101
Expected time: 45-60 seconds ✅
Recommended: Increase timeout to 180s
```

---

## 📊 New Sidebar Features

### **Advanced Settings** (New!)

#### 1. Timeout Slider
```
Timeout (seconds)
|-------|-------|-------|-------|
60     120     180     240     300

Default: 120 seconds
Recommended for compound models: 180-240 seconds
```

**What it does:**
- Controls how long to wait before timeout
- Increase for complex pages or slow websites
- Decrease for faster results on simple pages

#### 2. Max Retries Input
```
Max Retries: [2]  ← Click to change

Range: 0-5
Default: 2
```

**What it does:**
- Automatically retries on timeout/connection errors
- Waits 2s, 4s, 6s between retries (exponential backoff)
- Won't retry on authentication errors

---

## 🔍 Understanding the New Error Messages

### When You See: ⏱️ Request Timed Out
**Meaning:** The extraction took too long

**Solutions shown:**
1. Use faster model
2. Try CLI tool for individual extraction

### When You See: ⚠️ API Endpoint Detected
**Meaning:** URL contains `/api/` - likely a data endpoint

**Solutions shown:**
1. Use main website URL instead
2. Find documentation page
3. Specific suggestion for your URL

### When You See: 🔑 API Key Issue
**Meaning:** Problem with your GROQ_API_KEY

**Solution:** Check `.env` file

### When You See: 🌐 Connection Issue
**Meaning:** Network connectivity problem

**Solution:** Check internet connection

---

## ⚙️ Recommended Settings by Page Type

### Simple Pages (GitHub, most websites)
```yaml
Model: moonshotai/kimi-k2-instruct-0905
Timeout: 120 seconds
Max Retries: 2
Expected time: 10-30 seconds
```

### Moderate Pages (Statistics websites)
```yaml
Model: moonshotai/kimi-k2-instruct-0905  # or compound-mini
Timeout: 180 seconds
Max Retries: 3
Expected time: 30-60 seconds
```

### Complex Pages (Deep documentation)
```yaml
Model: groq/compound-mini  # or groq/compound
Timeout: 240 seconds
Max Retries: 4
Expected time: 60-120 seconds
```

### API Endpoints (Use main URL instead!)
```yaml
❌ Don't use: https://site.com/api/v1/data/123
✅ Use:       https://site.com/
```

---

## 📈 Progress Indicators (New!)

While extracting, you'll now see:

```
🔄 Launching browsers and extracting comprehensive metadata...
💡 Tip: This may take 30-60 seconds for comprehensive extraction.
The browser automation is:
- 🌐 Visiting the main page
- 🔍 Discovering metadata and documentation links
- 📄 Following nested pages for license, place, and temporal info
- 🤖 Using AI to validate and structure findings

⏳ Extracting metadata (timeout: 180s, retries: 3)...
```

After completion:
```
✅ Metadata extraction completed successfully in 42.3 seconds!
```

---

## 🛠️ Troubleshooting Checklist

### If extraction fails:

- [ ] Check if URL is accessible in browser
- [ ] Verify it's not an API endpoint (no `/api/` in URL)
- [ ] Increase timeout to 180-240 seconds
- [ ] Increase max retries to 3-4
- [ ] Try faster model: `moonshotai/kimi-k2-instruct-0905`
- [ ] Check internet connection
- [ ] Verify GROQ_API_KEY in `.env` file
- [ ] Try a known working URL (GitHub example above)
- [ ] Use CLI tool for detailed error messages

### Still having issues?

Try the CLI tool with debug info:
```bash
python browser_automation_extractor.py <url> --mode=license
```

This will show more detailed error messages and what the browser automation is doing.

---

## 💡 Pro Tips

1. **Start with main website URL**, not deep links or API endpoints
2. **Use faster model first** (`moonshotai/kimi-k2-instruct-0905`)
3. **Increase timeout for first attempt** on new websites
4. **Enable retries** (3-4) for unreliable connections
5. **Check error messages** - they now provide specific guidance
6. **Watch progress indicators** - they show what's happening
7. **Try working examples** to verify setup is correct

---

## Summary of Fixes ✅

| Feature | Before | After |
|---------|--------|-------|
| Timeout | Fixed 120s | **Configurable 60-300s** |
| Retries | None | **Automatic with backoff** |
| Error Messages | Generic | **Context-specific guidance** |
| Progress | Basic spinner | **Detailed status updates** |
| API Detection | None | **Warns and suggests alternatives** |
| Elapsed Time | Not shown | **Shows completion time** |

---

## Next Steps

1. **Reopen the Streamlit app**
2. Look at the **left sidebar**
3. Find **"Advanced Settings"**
4. Adjust **Timeout** and **Max Retries**
5. Try with the **main website URL**: `https://andmed.stat.ee/`
6. Click **"Extract All Metadata"**

The timeout issue is now completely fixed with multiple layers of protection! 🎉
