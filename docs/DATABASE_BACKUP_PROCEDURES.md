# Database Backup Procedures

**CRITICAL: Always backup databases before making ANY changes**

## Databases on Railway

The following databases are stored in `/data` on Railway (persistent volume):

- `/data/print_ordering.db` - Contains Shopify product mappings, print notifications, and order data
- `/data/pricing.db` - Contains pricing information for print products
- `/data/image_descriptions.json` - Contains all image descriptions

## Before Making Changes

**ALWAYS run these commands BEFORE making any changes to the system:**

```bash
# Backup print_ordering.db
cp /data/print_ordering.db /data/print_ordering.db.backup.$(date +%Y%m%d_%H%M%S)

# Backup pricing.db
cp /data/pricing.db /data/pricing.db.backup.$(date +%Y%m%d_%H%M%S)

# Backup image_descriptions.json
cp /data/image_descriptions.json /data/image_descriptions.json.backup.$(date +%Y%m%d_%H%M%S)
```

## Restoring from Backup

If something goes wrong, restore from the most recent backup:

```bash
# Restore print_ordering.db
cp /data/print_ordering.db.backup.YYYYMMDD_HHMMSS /data/print_ordering.db

# Restart the application
# (Railway will automatically restart on file changes)
```

## Important Rules

1. **NEVER commit database files to git** - Add `*.db` to `.gitignore`
2. **NEVER push `/data` directory to git** - It's Railway-specific
3. **ALWAYS create timestamped backups before changes**
4. **Keep at least 7 days of backups** - Delete older ones to save space

## Automated Backup Script

Create a backup script that runs before any admin operation:

```python
import shutil
from datetime import datetime

def backup_databases():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    databases = [
        '/data/print_ordering.db',
        '/data/pricing.db',
        '/data/image_descriptions.json'
    ]
    
    for db in databases:
        if os.path.exists(db):
            backup_path = f"{db}.backup.{timestamp}"
            shutil.copy2(db, backup_path)
            print(f"Backed up {db} to {backup_path}")
```

## Recovery Checklist

If data is lost:

1. Check `/data` for `.backup.*` files
2. Identify the most recent backup before the issue
3. Copy the backup file over the current database
4. Restart the application
5. Verify data integrity
6. Document what caused the data loss to prevent recurrence
