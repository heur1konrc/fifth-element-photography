# Railway Deployment Verification Checklist

## Deployment Status
- **Commit**: b87091d - "Simplify pricing setup - use pre-populated database template"
- **Date**: October 30, 2025
- **Status**: Building...

## Changes Deployed
1. Created pre-populated database template: `database_templates/print_ordering_initial.db`
2. Simplified setup route to copy template instead of importing from Excel
3. Removed dependency on Excel parsing in production environment

## Verification Steps

### Step 1: Database Initialization
- [ ] Visit: `https://your-site.up.railway.app/admin/setup-pricing`
- [ ] Click "Initialize Database" button
- [ ] Expected result: Success message showing "156 products initialized"
- [ ] Database should be created at: `/data/print_ordering.db`

### Step 2: Pricing Admin Dashboard
- [ ] Visit: `https://your-site.up.railway.app/admin/pricing`
- [ ] Expected result: Dashboard showing product counts by category:
  - Canvas: 16 products
  - Framed Canvas: 36 products
  - Fine Art Paper: 52 products
  - Foam-mounted: 52 products
  - **Total: 156 products**

### Step 3: Browse Pricing
- [ ] Click "Browse Pricing" from dashboard
- [ ] Filter by different categories
- [ ] Verify products display with:
  - Product name
  - Size
  - Cost price
  - Retail price (should equal cost since no markup applied yet)
  - Availability status

### Step 4: Manage Markups
- [ ] Click "Manage Markups" from dashboard
- [ ] View current markup settings (should all be 0% or 1.0x)
- [ ] Test updating a markup (don't save if you don't want to change yet)
- [ ] Verify markup calculation preview works

### Step 5: Manage Products
- [ ] Click "Manage Products" from dashboard
- [ ] View product list with enable/disable toggles
- [ ] Verify all products show correct Lumaprints API IDs
- [ ] Test filtering by category

## Database Template Contents

The `print_ordering_initial.db` template includes:

### Product Categories (4)
- 101: Canvas
- 102: Framed Canvas
- 103: Fine Art Paper
- 104: Foam-mounted

### Product Subcategories (15)
**Canvas (4):**
- 101001: 0.75" wrap
- 101002: 1.25" wrap
- 101003: 1.50" wrap
- 101005: Rolled

**Framed Canvas (3):**
- 102001: 0.75" depth
- 102002: 1.25" depth
- 102003: 1.50" depth

**Fine Art Paper (4):**
- 103002: Hot Press
- 103003: Cold Press
- 103005: Semi-Glossy
- 103007: Glossy

**Foam-mounted (4):**
- 104002: Hot Press
- 104003: Cold Press
- 104005: Semi-Glossy
- 104007: Glossy

### Print Sizes
- Multiple aspect ratios: 1:1, 3:2, 2:3, 4:3, 3:4, 16:9, 9:16
- Size range: 4x4 to 60x90 inches
- Total unique sizes across all products: varies by category

### Base Pricing (156 records)
- All products have cost prices from Lumaprints wholesale catalog
- No markup applied (markup_multiplier = 1.0)
- All products enabled by default (is_available = TRUE)

## Troubleshooting

### If initialization fails:
1. Check Railway logs for error messages
2. Verify `/data` directory exists and is writable
3. Verify `database_templates/print_ordering_initial.db` was deployed
4. Check file permissions on Railway volume

### If pricing admin shows no products:
1. Verify database was initialized successfully
2. Check database path in `routes/pricing_admin.py`
3. Verify database connection is working
4. Check Railway logs for SQL errors

### If products display incorrectly:
1. Verify database schema matches expected structure
2. Check foreign key relationships
3. Verify Lumaprints API IDs are correct

## Next Steps After Verification

Once all verification steps pass:

1. **Set Markup Strategy**
   - Decide on markup approach (global vs. category-specific)
   - Update markups in admin interface
   - Verify retail prices calculate correctly

2. **Curate Product Selection**
   - Review all 156 products
   - Disable products you don't want to offer
   - Focus on most popular sizes

3. **Test Lumaprints API**
   - Test API connection with sandbox credentials
   - Verify product IDs match Lumaprints catalog
   - Test order submission (sandbox mode)

4. **Begin Customer-Facing Development**
   - Design product selection UI
   - Build shopping cart functionality
   - Integrate payment processing
   - Connect to OrderDesk

## Support

If you encounter issues:
- Check Railway deployment logs
- Review `/home/ubuntu/fifth-element-photography/PRINT_ORDERING_SYSTEM_PLAN.md`
- Reference API documentation in `LUMAPRINTS_API_NOTES.md` and `ORDERDESK_API_NOTES.md`

