# Revert Instructions for Price Sync Mapping Fix

**Date:** December 25, 2025
**File Modified:** `routes/shopify_price_sync_api.py`
**Backup Location:** `routes/shopify_price_sync_api.py.backup_20251225_020247`

## What Was Changed

Updated the `map_product_type_to_shopify()` function in `shopify_price_sync_api.py` to include complete mappings for:
- Canvas products (0.75", 1.25", 1.50" Stretched and Framed)
- Metal products (Glossy White Metal, Glossy Silver Metal)
- Rolled Canvas

This matches the mapping function in `shopify_api_creator.py` exactly.

## How to Revert

If the fix causes issues, run these commands:

```bash
cd /home/ubuntu/fifth-element-photography
cp routes/shopify_price_sync_api.py.backup_20251225_020247 routes/shopify_price_sync_api.py
git add routes/shopify_price_sync_api.py
git commit -m "Revert price sync mapping fix"
git push
```

## What This Does NOT Affect

- ✅ Lumaprints Bulk Mapping (completely separate system)
- ✅ Create Shopify Products (already has correct mapping)
- ✅ Database structure
- ✅ Existing Shopify products

## What This DOES Fix

- ✅ Price sync now matches Canvas products correctly
- ✅ Price sync now matches Metal products correctly
- ✅ All 72 previously failing variants should now sync successfully
