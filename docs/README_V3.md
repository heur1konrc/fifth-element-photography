# Fifth Element Photography - Admin V3

**Version:** 3.0.0-alpha  
**Status:** In Development

## Overview

Admin V3 is a complete rewrite of the Fifth Element Photography admin dashboard, built from scratch with a focus on clean code, maintainability, and comprehensive documentation. It provides a robust and scalable platform for managing the image gallery, categories, and metadata.

## Features

- **Image Management:** Upload, delete, rename, and describe images.
- **Category System:** Assign multiple categories per image, create/delete categories.
- **Filtering & Sorting:** Filter images by category and sort by various criteria.
- **Clean Architecture:** Separation of concerns between backend, frontend, and data.
- **Full Documentation:** Every part of the system is documented.

## Getting Started

### Prerequisites

- Python 3.10+
- Flask
- Git

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/heur1konrc/fifth-element-photography.git
    cd fifth-element-photography
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Run the V3 application:
    ```bash
    python app_v3.py
    ```

### Testing

1.  Switch to the `v3-staging` branch:
    ```bash
    git checkout v3-staging
    ```

2.  Deploy to Railway (or run locally).
3.  Access the admin dashboard at `/admin_v3`.

## Documentation

- **Architecture:** [ARCHITECTURE_V3.md](ARCHITECTURE_V3.md)
- **API Reference:** [API_V3.md](API_V3.md)
- **Changelog:** [CHANGELOG_V3.md](CHANGELOG_V3.md)

## Contributing

Please follow the development workflow outlined in the project structure document.

