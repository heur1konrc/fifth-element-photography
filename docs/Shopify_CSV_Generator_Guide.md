# Shopify CSV Generator: User Guide

**Version 1.0**

## 1. Introduction

This tool automates the creation of Shopify product CSVs, reducing the time it takes to add new images for sale from hours to minutes. It automatically detects aspect ratios, queries your pricing database, and generates a Shopify-compatible CSV with all product variants and correct pricing.

## 2. How it Works

1.  **Select Images**: Choose one or more images from your gallery.
2.  **Generate CSV**: The tool creates a CSV file with all product variants for the selected images.
3.  **Upload to Shopify**: Import the CSV into Shopify to create the products instantly.

## 3. Step-by-Step Guide

1.  **Navigate to the Admin Panel**: Go to `/admin`.
2.  **Open the Shopify CSV Generator**: Click the green **"Generate Shopify CSV"** button.
3.  **Select Images**: In the modal, check the boxes next to the images you want to create products for. You can use the "Select All" checkbox to select all images at once.
4.  **Generate & Download**: Click the **"Generate & Download CSV"** button. The tool will process the images and your browser will download the CSV file.
5.  **Upload to Shopify**: Log in to your Shopify admin, go to **Products**, and click **Import**. Upload the CSV file you just downloaded.

## 4. What it Generates

The tool automatically creates product variants for:

*   **Fine Art Paper** (Hot Press, Semi-glossy, Glossy)
*   **Canvas** (0.75" Stretched Canvas)

It includes all size variants based on the image's aspect ratio (Standard 3:2 or Square 1:1) and calculates prices using your current global markup from the pricing database.
