# Admin V3 - Testing Guide

**Version**: 3.0.0-alpha  
**Status**: Ready for Testing  
**Date**: December 20, 2024

---

## Overview

Admin V3 is now complete and ready for your testing. This guide will help you understand what's been built, how to deploy it, and what to test.

## What's Been Built

The V3 admin rebuild includes **2,315 lines of clean, documented code** across the following components:

### Backend Infrastructure
- **data_manager_v3.py** (316 lines): Complete data access layer for images, metadata, and categories
- **app_v3.py** (318 lines): Flask application with authentication and REST API routes

### Admin Dashboard
- **admin_v3.html** (155 lines): Clean HTML structure with semantic markup
- **admin_v3.css** (543 lines): Modern, responsive styles
- **admin_v3.js** (529 lines): Full interactive functionality

### Test Front-End
- **login_v3.html** (121 lines): Clean login page
- **index_v3.html** (33 lines): Simple gallery structure
- **index_v3.css** (188 lines): Responsive gallery styles
- **index_v3.js** (112 lines): Image fetching and display

### Documentation
- **README_V3.md**: Project overview and setup instructions
- **ARCHITECTURE_V3.md**: System design and data flow
- **CHANGELOG_V3.md**: Complete version history
- **V3_PROJECT_STRUCTURE.md**: File organization
- **V3_TESTING_GUIDE.md**: This document

---

## Deployment Instructions

### Step 1: Switch Railway to v3-staging Branch

1. Go to your Railway project dashboard
2. Navigate to your deployment settings
3. Change the branch from `main` to `v3-staging`
4. Railway will automatically redeploy with the V3 code

**Important**: The `/data/` directory will remain intact during this switch. All existing images and metadata will be preserved.

### Step 2: Access the V3 Admin

Once deployed, you can access:

- **Public Front-End**: `https://your-railway-url.com/`
- **Admin Login**: `https://your-railway-url.com/login_v3`
- **Admin Dashboard**: `https://your-railway-url.com/admin_v3` (requires login)

### Step 3: Login Credentials

Use the admin credentials set in your Railway environment variables:
- **Username**: Value of `ADMIN_USERNAME` (default: `admin`)
- **Password**: Value of `ADMIN_PASSWORD` (default: `password`)

---

## What to Test

### 1. Admin Dashboard Access
- [ ] Can you access `/login_v3` and see the login page?
- [ ] Can you log in with your credentials?
- [ ] Are you redirected to `/admin_v3` after login?
- [ ] Can you see the admin dashboard interface?

### 2. Image Upload
- [ ] Can you drag and drop an image to upload?
- [ ] Can you click "Browse Files" to select an image?
- [ ] Does the upload show progress/success message?
- [ ] Does the uploaded image appear in the gallery?

### 3. Image Editing
- [ ] Can you click "Edit" on an image?
- [ ] Can you change the title?
- [ ] Can you change the description?
- [ ] Can you add categories to the image?
- [ ] Can you remove categories from the image?
- [ ] Do changes save correctly?

### 4. Image Deletion
- [ ] Can you click "Delete" on an image?
- [ ] Does a confirmation modal appear?
- [ ] Does the image delete when you confirm?
- [ ] Is the image removed from the gallery?

### 5. Category Management
- [ ] Can you create a new category?
- [ ] Does the new category appear in the category list?
- [ ] Can you delete a category?
- [ ] Is the category removed from all images when deleted?

### 6. Filtering
- [ ] Can you filter images by category?
- [ ] Does "All Images" show all images?
- [ ] Do category filters show only images with that category?

### 7. Sorting
- [ ] Can you sort by "Newest First"?
- [ ] Can you sort by "Oldest First"?
- [ ] Can you sort by "Name (A-Z)"?
- [ ] Can you sort by "Name (Z-A)"?
- [ ] Do the images reorder correctly?

### 8. Pagination
- [ ] If you have more than 20 images, does pagination appear?
- [ ] Can you navigate between pages?
- [ ] Do page numbers work correctly?

### 9. Front-End Display
- [ ] Can you access the public front-end at `/`?
- [ ] Do images display in the gallery?
- [ ] Do titles and descriptions show correctly?
- [ ] Do category badges appear?
- [ ] Is the layout responsive on mobile?

### 10. Logout
- [ ] Can you log out from the admin dashboard?
- [ ] Are you redirected to the login page?
- [ ] Can you not access `/admin_v3` after logout?

---

## Known Limitations

The following features are **not yet implemented** (planned for future phases):

1. **Shopify Product Mapping Tool**: Not included in this version
2. **Lumaprints Integration**: Not included in this version
3. **Automated Backup System**: Manual git backups only
4. **Production Front-End**: Current front-end is basic test version
5. **Image Randomization**: Not yet implemented on front-end

---

## Reporting Issues

When you find issues during testing, please provide:

1. **What you were trying to do**: Describe the action
2. **What happened**: Describe the actual behavior
3. **What you expected**: Describe the expected behavior
4. **Browser**: Which browser you're using
5. **Screenshots**: If applicable

I'll be ready to fix issues in real-time during your testing session.

---

## Next Steps After Testing

Once testing is complete and all issues are fixed:

1. **Tag the release**: Create git tag `v3.0.0-alpha`
2. **Create backup branch**: `v3-staging-backup-YYYYMMDD`
3. **Plan next phase**: Shopify Product Mapping tool
4. **Build production front-end**: Enhanced gallery with filters
5. **Add Lumaprints integration**: Print ordering system
6. **Production cutover**: Switch main branch to V3

---

## Emergency Rollback

If something goes wrong and you need to roll back:

1. Go to Railway dashboard
2. Change branch back to `main`
3. Railway will redeploy the old production code
4. Your `/data/` directory will remain intact

**No data will be lost** - the V3 code only reads/writes to the same `/data/` directory as the old code.

---

## Questions?

If you have questions during testing, I'm here and ready to help. Let's make this work perfectly before moving to the next phase.

---

**Ready to test? Switch Railway to `v3-staging` and let's go!** 🚀

