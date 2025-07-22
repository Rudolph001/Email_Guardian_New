# Dashboard Template Fix for Local Environment

## Problem
Your local dashboard template at `/Users/rudolph.vanstaden/Documents/Email_Guardian_New/templates/dashboard.html` still has the old attribute access syntax that causes the Jinja template error: `'dict object' has no attribute 'risk_distribution'`

## Solution
Replace the problematic lines in your local `templates/dashboard.html` file:

### Line 384 (or around line 384)
**FIND:**
```html
<span class="fw-bold text-danger animated-number" id="highRiskAttachments" data-target="{{ attachment_analytics.risk_distribution.high_risk_count or 0 }}">0</span>
```

**REPLACE WITH:**
```html
<span class="fw-bold text-danger animated-number" id="highRiskAttachments" data-target="{{ attachment_analytics.get('risk_distribution', {}).get('high_risk_count', 0) }}">0</span>
```

### Additional Template Fixes
Find and replace ALL instances of `attachment_analytics.` followed by direct attribute access in your `templates/dashboard.html`:

1. **Total Attachments (around line 380):**
```html
<!-- CHANGE THIS: -->
{{ attachment_analytics.total_attachments or 0 }}
<!-- TO THIS: -->
{{ attachment_analytics.get('total_attachments', 0) }}
```

2. **Average Risk Score (around line 388):**
```html
<!-- CHANGE THIS: -->
{{ "%.2f"|format(attachment_analytics.risk_distribution.mean_risk or 0) }}
<!-- TO THIS: -->
{{ "%.2f"|format(attachment_analytics.get('risk_distribution', {}).get('mean_risk', 0)) }}
```

3. **Malware Indicators (around line 396-400):**
```html
<!-- CHANGE THIS: -->
{% if attachment_analytics.malware_indicators %}
    {% for indicator, count in attachment_analytics.malware_indicators.items() %}
<!-- TO THIS: -->
{% if attachment_analytics.get('malware_indicators') %}
    {% for indicator, count in attachment_analytics.get('malware_indicators', {}).items() %}
```

## Quick Fix Script
You can also create a backup and apply this fix automatically:

```bash
cd /Users/rudolph.vanstaden/Documents/Email_Guardian_New

# Create backup
cp templates/dashboard.html templates/dashboard.html.backup

# Apply fixes
sed -i '' 's/attachment_analytics\.total_attachments/attachment_analytics.get('\''total_attachments'\'', 0)/g' templates/dashboard.html
sed -i '' 's/attachment_analytics\.risk_distribution\.high_risk_count/attachment_analytics.get('\''risk_distribution'\'', {}).get('\''high_risk_count'\'', 0)/g' templates/dashboard.html
sed -i '' 's/attachment_analytics\.risk_distribution\.mean_risk/attachment_analytics.get('\''risk_distribution'\'', {}).get('\''mean_risk'\'', 0)/g' templates/dashboard.html
sed -i '' 's/attachment_analytics\.malware_indicators/attachment_analytics.get('\''malware_indicators'\'')/g' templates/dashboard.html
```

## Why This Fix Works
The issue occurs because `attachment_analytics` is passed as a Python dictionary to the template, but the template was trying to access it like an object with attributes (using dot notation). The `.get()` method safely accesses dictionary keys and provides fallback values when keys don't exist.

## After Applying the Fix
1. Save the template file
2. Restart your local Flask application
3. Upload a CSV file in Chrome browser
4. The dashboard should now load without template errors

## Alternative: Route Handler Fix
If you want to keep the template syntax simple, you can also fix this in your local `routes.py` file by ensuring `attachment_analytics` is always a proper object structure, but the template fix above is simpler and more robust.