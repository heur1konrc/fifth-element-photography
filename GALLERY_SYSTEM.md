# Gallery System Documentation

## Overview
The gallery system allows organizing images into themed collections (Animals, Landscape, Nature, Portrait, Sports, etc.) with individual gallery pages accessible from the main navigation menu.

## Database Structure
- **galleries.db** (SQLite) stored in `/data/` directory
- Tables:
  - `galleries`: Stores gallery metadata (name, slug, hero_image, description, display_order, visible)
  - `gallery_images`: Many-to-many relationship between galleries and images

## Gallery Management

### Creating Galleries
Use the admin interface at `/admin/galleries` or via Python:

```python
from gallery_db import create_gallery

gallery_id = create_gallery(
    name='Animals',
    slug='animals',
    hero_image='wildlife_hero.jpg',  # optional
    description='Wildlife and animal photography',
    display_order=1
)
```

### Adding Images to Galleries
Via admin interface or Python:

```python
from gallery_db import add_image_to_gallery

add_image_to_gallery(
    gallery_id=1,
    image_filename='elephant.jpg',
    display_order=0  # optional
)
```

### Gallery URLs
- Homepage: `/`
- Individual gallery: `/gallery/{slug}` (e.g., `/gallery/animals`)
- Admin interface: `/admin/galleries`

## Gallery Page Features
1. **Hero Image** - Large banner image at top (optional)
2. **Image Grid** - Responsive grid of images assigned to the gallery
3. **Navigation** - Menu with all visible galleries
4. **Responsive Design** - Max width 1440px, fluid down to mobile

## Image Optimization
- Gallery pages use **gallery-images** (1200px width) for performance
- Hero images also use gallery-images format
- Original full-resolution images remain in `/data/` for printing

## API Endpoints
- `GET /api/galleries` - List all galleries
- `POST /api/galleries` - Create new gallery
- `PUT /api/galleries/<id>` - Update gallery
- `DELETE /api/galleries/<id>` - Delete gallery
- `POST /api/galleries/<id>/images` - Add images to gallery
- `DELETE /api/galleries/<id>/images/<filename>` - Remove image from gallery

## Integration with Existing System
- Galleries appear in main navigation menu automatically
- Uses existing image management system
- Compatible with carousel system (separate feature)
- Works with EXIF data and image metadata
