# Backup Log - Fifth Element Photography
**Version:** v1.0.0  
**Created:** 2025-10-27  
**Purpose:** Track all incremental backups for rollback capability

---

## Backup History

### backup_20251027_221047_pre_cleanup.tar.gz
- **Date:** 2025-10-27 22:10:47 UTC
- **Size:** 3.9 MB
- **Description:** Full backup before removing print ordering system and databases
- **State:** Complete working site with print ordering, pricing database, admin tools, and gallery
- **Location:** `/home/ubuntu/fifth-element-photography/backups/`
- **Can restore to:** Full print ordering functionality (broken state from morning issues)
- **Notes:** This is the state BEFORE cleanup. Includes all pricing code, databases, and ordering forms.

---

## How to Restore a Backup

```bash
cd /home/ubuntu/fifth-element-photography
tar -xzf backups/backup_YYYYMMDD_HHMMSS_description.tar.gz
git add -A
git commit -m "RESTORE: from backup_YYYYMMDD_HHMMSS_description"
git push origin main
```

---

## Backup Rules
1. Create backup BEFORE any major work or edits
2. Name format: `backup_YYYYMMDD_HHMMSS_description.tar.gz`
3. Document in this log immediately
4. Store in `/backups/` directory
5. Never delete backups without explicit permission

