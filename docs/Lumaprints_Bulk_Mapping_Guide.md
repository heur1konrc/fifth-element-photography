'''
# How to Use the Lumaprints Bulk Mapping Tool

**Author:** Manus AI
**Date:** December 05, 2025

---

## 1. Introduction

The Lumaprints Bulk Mapping tool is designed to save you hours of manual work by automating the process of linking your gallery images to products in your Lumaprints export file. Instead of mapping each product variation one by one, this tool allows you to map a single image to a product *title*. The system then automatically applies that mapping to all associated product types and sizes for that title, including Canvas and all three types of Art Paper.

This guide provides a step-by-step walkthrough of how to use the tool effectively.

---

## 2. Before You Begin: Get the Lumaprints File

Before using the tool, you must first export your product data from your Lumaprints account.

1.  Log in to your Lumaprints dashboard.
2.  Navigate to the product export section.
3.  Download your product list as an **`.xlsx`** file.

This is the file you will upload into the admin tool.

---

## 3. Step-by-Step Guide

The entire process is handled within a single modal window in your admin dashboard, broken down into three simple steps.

### Step 1: Access the Tool and Upload Your File

First, open the Bulk Mapping tool from your admin dashboard.

1.  Navigate to your **Admin Dashboard**.
2.  In the main toolbar, click the **Lumaprints Bulk Mapping** button. This will open the mapping tool modal.

    ![Bulk Mapping Button](https://i.imgur.com/your-button-image.png) <!-- Placeholder: Replace with actual image if available -->

3.  Inside the modal, you will be at **Step 1: Upload Lumaprints Excel File**.
4.  Click the **Choose File** button and select the `.xlsx` file you downloaded from Lumaprints.
5.  Click the **Upload & Process** button.

    The system will analyze the file to find all "Unmapped" products. You will see a status message confirming how many unmapped products were found. The tool will then automatically proceed to the next step.

### Step 2: Map Images to Products

This is the core step where you link your images to the product titles from the Excel file.

1.  The interface will now show **Step 2: Map Images to Products**.
2.  You will see a **Batch Mapping Form**. This is where you create the links between your gallery images and the Lumaprints product titles.
3.  For each mapping, you need to fill in three fields:
    *   **Product Title:** Select the product title from the dropdown menu. This list is populated directly from your uploaded Excel file.
    *   **Image Filename:** Enter the exact filename of the corresponding image in your gallery (e.g., `my-awesome-photo.jpg`).
    *   **Aspect Ratio:** Choose the correct aspect ratio for the image (`3:2`, `2:3`, or `1:1`). This ensures the mapping applies to the correct product variations.

4.  If you need to map more than one product title, click the **+ Add Another Mapping** button to add more rows.

    ![Mapping Form](https://i.imgur.com/your-form-image.png) <!-- Placeholder: Replace with actual image if available -->

> **Important:** The power of this tool is its automation. When you map a title like "Mountain Sunset", the tool automatically finds every product variation associated with that title (e.g., 0.75in Stretched Canvas, Hot Press Fine Art Paper, etc.) and applies the image mapping to all of them. You do not need to map each one individually.

### Step 3: Apply Mappings and Download

Once you have added all your desired mappings, you are ready to finalize the process.

1.  After filling out your mapping rows, click the **✓ Apply All Mappings** button.
2.  The system will process your mappings and apply them to the in-memory version of your Excel file. You will automatically be taken to the final step.
3.  You are now at **Step 3: Download Mapped File**.
4.  The screen will show a success message confirming how many products were mapped.
5.  Click the **Download Excel File** button.

    A new `.xlsx` file named `lumaprints_mapped.xlsx` will be downloaded to your computer.

---

## 4. Final Step: Upload to Lumaprints

Your work in the admin tool is now complete. The final step is to upload the newly generated file back into Lumaprints to update your products.

1.  Return to your Lumaprints dashboard.
2.  Navigate to the product import section.
3.  Upload the `lumaprints_mapped.xlsx` file.

Lumaprints will process the file, and your images will now be correctly linked to your products.
'''
