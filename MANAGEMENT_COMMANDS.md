# Management Commands Documentation

## import_recipients

This management command allows you to bulk import recipients from CSV or Excel files via the command line.

### Usage

```bash
python manage.py import_recipients <file_path> [options]
```

### Arguments

- `file_path` - Path to the CSV or Excel file to import (required)

### Options

- `--update-existing` - Update existing recipients instead of skipping them
- `--dry-run` - Preview import without making changes
- `--help` - Show help message

### Examples

```bash
# Preview import without making changes
python manage.py import_recipients recipients.csv --dry-run

# Import with real changes
python manage.py import_recipients recipients.csv

# Import and update existing recipients
python manage.py import_recipients recipients.xlsx --update-existing

# Import Excel file with dry run and update existing
python manage.py import_recipients data.xlsx --dry-run --update-existing
```

### File Format

The file should have the same format as required by the admin interface:
- Required headers: Display name, First name, Last name
- Optional headers: Email

### Output

The command provides detailed output including:
- Progress for each recipient processed
- Summary of created, updated, and skipped recipients
- Error messages for any issues encountered

### Exit Codes

- `0` - Success
- `1` - Error (file not found, validation failed, etc.)

### Use Cases

- **Automated imports** - Schedule regular imports from external systems
- **Large datasets** - Import large files that might timeout in the web interface
- **Scripted workflows** - Integrate with deployment or data migration scripts
- **Testing** - Validate data before importing through the admin interface
