# Bugs to Fix

## 1. Aspect Ratio Display
**Issue**: 6000x4000 shows as "1.50 aspect ratio" instead of "3:2"
**Location**: `templates/order_form.html` - displaySizes() function, line ~392
**Fix**: Convert decimal to proper ratio format (e.g., 1.5 → 3:2, 1.33 → 4:3)

