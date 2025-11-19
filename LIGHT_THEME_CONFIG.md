# Light Theme Configuration - Streamlit

## Overview

This document explains how the light theme is enforced in the Metadata Extractor application using Streamlit's configuration system.

---

## Configuration Location

**File:** `.streamlit/config.toml`

This file is automatically loaded by Streamlit when the app starts and applies the theme settings.

---

## Theme Settings

### Current Configuration

```toml
[theme]
base = "light"
primaryColor = "#2563eb"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f9fafb"
textColor = "#000000"
font = "sans serif"
```

### Color Breakdown

| Setting | Value | Purpose |
|---------|-------|---------|
| `base` | `"light"` | Forces light theme as default |
| `primaryColor` | `#2563eb` | Blue accent for buttons, links, active states |
| `backgroundColor` | `#ffffff` | Pure white main content area |
| `secondaryBackgroundColor` | `#f9fafb` | Light gray for sidebar and widgets |
| `textColor` | `#000000` | Pure black text throughout |
| `font` | `"sans serif"` | Clean, professional font |

---

## How It Works

### 1. **Default Theme Enforcement**

When users open the app, it will always start in light mode regardless of their system preferences.

```toml
base = "light"
```

### 2. **Custom Theme Name**

With these settings, Streamlit displays the theme as **"Custom Theme"** in the settings menu, making it clear this is a designed theme.

### 3. **Consistent Colors**

The colors defined in `config.toml` work in conjunction with the CSS in `license_finder_app.py` to create a cohesive light theme:

- **config.toml** → Sets Streamlit's native component colors
- **Custom CSS** → Overrides specific elements for fine-grained control

---

## User Settings

### Can Users Still Switch to Dark Mode?

**Partially.** Here's what happens:

1. **Default Behavior:** App always opens in light mode
2. **Settings Menu:** Users can technically see theme options in Settings (☰ menu)
3. **But:** Your custom theme is applied by default
4. **System Preference:** The app ignores system dark mode preferences

### Settings Menu Location

Users can access theme settings via:
```
☰ Menu → Settings → Theme
```

They'll see:
- **Custom Theme** (your light theme - default)
- Light
- Dark

However, the custom theme will persist unless they manually change it.

---

## Benefits of This Approach

### ✅ Advantages

1. **Consistent Branding:** All users see the same professional light theme
2. **Accessibility:** Black-on-white text meets WCAG AAA standards
3. **Professional Appearance:** Appropriate for enterprise/government clients
4. **No Code Changes:** Works with existing CSS customizations
5. **Persistent:** Theme persists across sessions

### ⚠️ Limitations

1. **Cannot Fully Disable Dark Mode:** Streamlit doesn't allow removing the theme toggle
2. **User Can Override:** Determined users can still switch themes
3. **System Preference Ignored:** Some users expect dark mode if their system uses it

---

## Testing the Configuration

### Step 1: Restart the App

After creating `.streamlit/config.toml`, restart Streamlit:

```bash
# Stop current server (Ctrl+C)
# Then restart:
streamlit run license_finder_app.py
```

### Step 2: Verify Light Theme

When the app opens, you should see:
- ✓ White background
- ✓ Black text
- ✓ Blue primary buttons
- ✓ Light gray sidebar

### Step 3: Check Settings Menu

1. Click the **☰ menu** (top right)
2. Select **Settings**
3. Look at **Theme** section
4. Should show **"Custom Theme"** as selected

---

## Troubleshooting

### Issue: Dark Theme Still Appears

**Solution:**
1. Clear browser cache: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. Check `.streamlit/config.toml` exists in project root
3. Ensure `base = "light"` is set correctly
4. Restart Streamlit server

### Issue: Colors Don't Match

**Solution:**
Verify both configurations are aligned:

```toml
# .streamlit/config.toml
primaryColor = "#2563eb"
textColor = "#000000"
```

```python
# license_finder_app.py (CSS)
.stButton > button[kind="primary"] {
    background-color: #2563eb !important;
}
```

### Issue: Theme Resets to Dark

**Solution:**
- This shouldn't happen with `config.toml`
- If it does, check browser localStorage:
  - Open DevTools (F12)
  - Application → Local Storage
  - Clear Streamlit entries

---

## Advanced Customization

### Option 1: Completely Hide Theme Toggle

**Not officially supported,** but you can hide it with CSS:

```python
# Add to license_finder_app.py
st.markdown("""
    <style>
    /* Hide theme toggle */
    [data-testid="stHeader"] button[kind="header"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)
```

⚠️ **Warning:** This is a hack and may break in future Streamlit versions.

### Option 2: Custom Theme Presets

You can create multiple config files for different deployments:

```bash
.streamlit/
├── config.toml          # Production (light theme)
├── config.dark.toml     # Alternative (dark theme)
└── config.dev.toml      # Development (with debugging)
```

Load different configs:
```bash
# Use alternative config
streamlit run app.py --config .streamlit/config.dark.toml
```

---

## Deployment Considerations

### Local Development

The `config.toml` works automatically when running:
```bash
streamlit run license_finder_app.py
```

### Streamlit Cloud

1. Commit `.streamlit/config.toml` to your repo
2. Push to GitHub/GitLab
3. Deploy on Streamlit Cloud
4. Theme will be automatically applied

### Docker Deployment

Include in `Dockerfile`:
```dockerfile
COPY .streamlit /app/.streamlit
WORKDIR /app
CMD ["streamlit", "run", "license_finder_app.py"]
```

### Heroku / Other Platforms

Ensure `.streamlit/config.toml` is:
- ✓ Committed to git
- ✓ Not in `.gitignore`
- ✓ Deployed with application code

---

## Color Palette Reference

For consistency across all materials (documentation, slides, etc.):

### Primary Colors
```css
--primary-blue: #2563eb;
--primary-blue-dark: #1d4ed8;
```

### Neutral Colors
```css
--white: #ffffff;
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-300: #d1d5db;
--gray-500: #6b7280;
--gray-700: #374151;
--black: #000000;
```

### Semantic Colors
```css
--success: #22c55e;
--error: #ef4444;
--warning: #f59e0b;
--info: #3b82f6;
```

---

## Best Practices

### ✅ DO

1. Keep `config.toml` in version control
2. Use colors that meet accessibility standards
3. Test theme on different screen sizes
4. Document any theme changes in git commits
5. Match `config.toml` colors with custom CSS

### ❌ DON'T

1. Don't hardcode colors in Python strings (use CSS)
2. Don't assume users can't change theme (they can)
3. Don't use extremely bright or low-contrast colors
4. Don't forget to test after Streamlit updates
5. Don't mix multiple color systems (stick to one palette)

---

## Related Files

| File | Purpose |
|------|---------|
| `.streamlit/config.toml` | Theme configuration (this document) |
| `license_finder_app.py` | Custom CSS for fine-grained styling |
| `.env` | API keys and environment variables |
| `requirements.txt` | Python dependencies |

---

## Updates Log

| Date | Change | Reason |
|------|--------|--------|
| 2025-01-19 | Initial light theme config | Force light mode for professional appearance |
| 2025-01-19 | Set all text to black (#000000) | User requested pure black text |
| 2025-01-19 | Set background to pure white | Clean, minimal design |

---

## Support

### Streamlit Documentation

- **Theming:** https://docs.streamlit.io/develop/concepts/configuration/theming
- **Config Options:** https://docs.streamlit.io/develop/concepts/configuration/options
- **App Chrome:** https://docs.streamlit.io/develop/concepts/architecture/app-chrome

### Common Questions

**Q: Can I force users to only use light mode?**
A: Not completely. `config.toml` sets the default, but users can override in settings.

**Q: Will this work on mobile?**
A: Yes, the theme applies to all devices.

**Q: Does this affect performance?**
A: No, theming has negligible performance impact.

**Q: Can I use hex colors with alpha?**
A: No, use 6-digit hex codes only (#RRGGBB).

---

**Configuration Status:** ✅ Active
**Theme Version:** 1.0
**Last Updated:** 2025-01-19
