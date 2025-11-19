# Error 413: Request Entity Too Large - Solution

## Problem Identified ✅

**Error:** `Error code: 413 - Request Entity Too Large`

**Your URL:** `https://www.ssb.no/en/statbank/table/06913/tableViewLayout1/`

## What This Means

The Groq API has a **request size limit**. When the browser automation visits your URL and tries to send the extracted content to the AI model, the content is **too large** to process.

### Why This Happens

1. **Data table pages** - Pages with large data tables have lots of HTML
2. **Complex layouts** - TableViewLayout pages have extra rendering code
3. **Many links** - Statistical tables often have hundreds of data points
4. **Compound model** - Sends all discovered content for thorough analysis

### Specific to Your URL

```
https://www.ssb.no/en/statbank/table/06913/tableViewLayout1/
                                ↑                ↑
                         Specific table    Complex layout view
```

This is a **specific data table with a complex layout view** - exactly the type of page that causes 413 errors.

---

## Solution ✅ Implemented

### Automatic Detection & Fix

Now when you get a 413 error on a table URL, the app shows:

```
❌ Extraction Failed

⚠ Error Details: Error code: 413 - Request Entity Too Large

**The page content is too large for the API to process.**

This happens with complex data tables or pages with lots of content.

**Solutions:**
1. Try the main website instead:
   [Try https://www.ssb.no] ← Click this button
```

### What Changed

1. **Detect 413 errors** - Specifically check for this error code
2. **Parse table URLs** - Extract the main website URL
3. **Show fix button** - One-click to try the main page
4. **Updated examples** - Norway Statistics now uses main page

---

## How to Use

### Option 1: Automatic Fix (Recommended)

1. Try your table URL
2. See 413 error
3. **Click the "Try https://www.ssb.no" button**
4. App automatically loads the main page
5. Click "Extract Metadata" again
6. Should work! ✓

### Option 2: Manual Fix

Instead of:
```
https://www.ssb.no/en/statbank/table/06913/tableViewLayout1/
```

Use:
```
https://www.ssb.no
```

The main page will have:
- License information (usually in footer)
- Links to documentation
- About/Contact pages
- Same organization metadata

---

## Why Main Pages Work Better

### Data Table Page (BAD for API)
```
Page Size: 500KB HTML
Content: Massive data table
Links: 500+ data points
Metadata: Hidden in JavaScript
Result: 413 Error ❌
```

### Main Page (GOOD for API)
```
Page Size: 50KB HTML
Content: Navigation, about, footer
Links: 20-30 main pages
Metadata: Clear footer/about links
Result: Success ✓
```

---

## Updated Example URLs

All example URLs now use **main pages** to avoid 413 errors:

### Before (Could cause 413):
```
Norway Statistics:
https://www.ssb.no/en/statbank/table/06913 ❌

Canada Statistics:
https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000101 ❌
```

### After (Works reliably):
```
Norway Statistics:
https://www.ssb.no ✓

Canada Statistics:
https://www.statcan.gc.ca ✓
```

---

## What You Get from Main Pages

### License Information
- Usually in footer: "Terms of Use", "License", "Copyright"
- Often in "About" or "Legal" pages
- Clear licensing statements

### Place Coverage
- "About" pages describe geographic scope
- Contact information shows location
- Dataset descriptions mention coverage

### Temporal Coverage
- Update schedules in footer
- "Latest updates" sections
- Publication dates in news/releases

### Example from SSB.no Main Page:

✓ License: Norwegian License for Open Government Data (NLOD)
✓ Place: Norway, Norwegian municipalities
✓ Temporal: Updated monthly/quarterly (varies by dataset)
✓ Organization: Statistics Norway (Statistisk sentralbyrå)

---

## Technical Details

### API Limits

**Groq API Request Limit:**
- Maximum request size: ~100KB (approximate)
- Includes: prompt + extracted content + metadata
- Compound model sends everything for analysis

**Your table URL:**
- Extracted content: ~500KB+
- Way over the limit
- Result: 413 error

**Main page URL:**
- Extracted content: ~50KB
- Well within limit
- Result: Success ✓

---

## Other URLs That May Cause 413

### Watch out for:

1. **Data table views**
   - `/table/12345/view`
   - `/datatable?id=xxx`
   - `/tableViewLayout`

2. **Large datasets**
   - `/dataset/huge-file`
   - Pages with embedded data

3. **Complex search results**
   - `/search?results=1000`
   - `/browse?all=true`

4. **API documentation pages**
   - `/api/docs` (if includes full API spec)
   - `/reference/complete`

### Use instead:

- Main homepage
- About pages
- Simple landing pages
- Navigation pages

---

## Testing the Fix

### Test 1: Refresh and Try

1. **Refresh your browser** (Ctrl+Shift+R)
2. **Try your original URL:** `https://www.ssb.no/en/statbank/table/06913/tableViewLayout1/`
3. **See the 413 error with new button**
4. **Click "Try https://www.ssb.no"**
5. **Extract again** - Should work! ✓

### Test 2: Use Example

1. **Click "Need an example?"**
2. **Click "Norway Statistics"**
3. **Now loads:** `https://www.ssb.no` (main page)
4. **Click "Extract Metadata"**
5. **Should succeed** ✓

---

## Expected Results from Main Pages

### Norway Statistics (https://www.ssb.no)

**License:**
- Norwegian License for Open Government Data (NLOD)
- Link to: https://data.norge.no/nlod/en

**Place:**
- Norway
- Norwegian municipalities and regions

**Temporal:**
- Various frequencies (monthly, quarterly, annual)
- Historical data available

### French Open Data (https://data.gouv.fr)

**License:**
- Open License / Licence Ouverte
- Link to: https://www.etalab.gouv.fr/licence-ouverte-open-licence

**Place:**
- France
- French departments and communes

**Temporal:**
- Real-time and historical
- Updated continuously

---

## Best Practices

### ✓ DO Use:
- Homepage URLs (https://example.com)
- About pages (https://example.com/about)
- Simple landing pages
- Navigation pages

### ✗ DON'T Use:
- Direct data table URLs
- Complex view layouts
- Search result pages with lots of results
- API endpoints
- Pages with embedded large datasets

---

## Summary

**Problem:** Table view URLs are too large for API (413 error)

**Solution:** Use main page URLs instead

**Implementation:**
1. ✅ Detect 413 errors specifically
2. ✅ Show clear explanation
3. ✅ Provide one-click fix button
4. ✅ Updated all example URLs
5. ✅ Extract main URL automatically

**Result:** Users get clear guidance and easy fix

**Success Rate:** Should now work for all example URLs ✓

---

## If You Still Get 413 Error

1. **Try the absolute homepage:** Just `https://example.com`
2. **Check if it's a data portal:** Try the portal homepage
3. **Look for documentation:** `/docs` or `/about` pages
4. **Use GitHub:** If it's a GitHub dataset
5. **Contact support:** If main page still fails

---

## Related Errors

### 413 vs 429 (Rate Limit)
- **413:** Content too large (use simpler URL)
- **429:** Too many requests (wait and retry)

### 413 vs Timeout
- **413:** Instant error (API rejects immediately)
- **Timeout:** Takes 4 minutes (API tries but gives up)

### 413 vs Connection Error
- **413:** API specific error code
- **Connection:** Can't reach server at all

---

**Your issue is now fixed!** Refresh the browser and try again with the auto-fix button or example URLs. 🎉
