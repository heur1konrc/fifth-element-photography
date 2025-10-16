# Updated mobile-new route to match main route data loading
@app.route('/mobile-new')
def mobile_new():
    """Mobile layout with admin data - using same data loading as main route"""
    images = scan_images()
    categories = load_categories()
    
    # Get category counts (same as main route)
    category_counts = {}
    for category in categories:
        category_counts[category] = len([img for img in images if img['category'] == category])
    
    # Get featured image from featured_image.json (same as main route)
    featured_image = None
    featured_image_data = load_featured_image()
    if featured_image_data and featured_image_data.get('filename'):
        # Find the featured image in the images list
        for image in images:
            if image['filename'] == featured_image_data['filename']:
                featured_image = image
                break
    
    # If no featured image is set, fallback to first landscape image or first image (same as main route)
    if not featured_image:
        for image in images:
            if image['category'] == 'landscape':
                featured_image = image
                break
        if not featured_image and images:
            featured_image = images[0]
    
    # Extract EXIF data for featured image (same as main route)
    featured_exif = None
    if featured_image:
        image_path = os.path.join(IMAGES_FOLDER, featured_image['filename'])
        featured_exif = extract_exif_data(image_path)
        
        # SINGLE SOURCE: Story is always the same as description
        featured_image['story'] = featured_image.get('description', '')
    
    about_data = load_about_data()

    # Load hero image (same as main route)
    hero_image_data = load_hero_image()
    hero_image = None
    if hero_image_data and hero_image_data.get('filename'):
        # Find the hero image in the images list
        for image in images:
            if image['filename'] == hero_image_data['filename']:
                hero_image = image
                break
    
    return render_template("mobile_new.html",
                         images=images,
                         categories=categories,
                         category_counts=category_counts,
                         featured_image=featured_image,
                         featured_exif=featured_exif,
                         about_data=about_data,
                         hero_image=hero_image)
