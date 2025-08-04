# Bulk Import Recipients Feature

## Overview

The bulk import feature allows administrators to import multiple recipients at once using CSV, XLS, or XLSX files. This feature is accessible from the Django admin interface in the Recipients section.

## How to Access

1. Log into the Django admin interface
2. Navigate to **Email API** > **Recipients**
3. Click on **"Bulk Import Recipients"** button (located at the top right of the recipients list)
4. Or use the admin action **"Bulk import recipients from file"** from the actions dropdown

## File Format Requirements

### Required Headers (case-insensitive)
- **Display name** - The full display name for the recipient
- **First name** - The recipient's first name
- **Last name** - The recipient's last name

### Optional Headers
- **Email** - The recipient's email address (auto-generated if not provided)

### Supported File Formats
- `.csv` (Comma Separated Values)
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

### File Size Limit
- Maximum file size: 10MB

## Sample File Formats

### CSV Example
```csv
Display name,First name,Last name,Email
John Doe,John,Doe,john.doe@company.com
Jane Smith,Jane,Smith,
Dr. Alice Johnson,Alice,Johnson,alice.j@hospital.org
,Bob,Wilson,
Mary Elizabeth,Mary,Elizabeth,mary.elizabeth@school.edu
```

### Excel Example
| Display name | First name | Last name | Email |
|--------------|------------|-----------|-------|
| John Doe | John | Doe | john.doe@company.com |
| Jane Smith | Jane | Smith | |
| Dr. Alice Johnson | Alice | Johnson | alice.j@hospital.org |
| | Bob | Wilson | |
| Mary Elizabeth | Mary | Elizabeth | mary.elizabeth@school.edu |

## Import Behavior

### Email Generation
- If no email is provided, it will be auto-generated using the format: `firstname.lastname@example.com`
- If only first name is available: `firstname@example.com`
- If only last name is available: `lastname@example.com`
- If duplicate emails are generated, a number will be appended (e.g., `john.doe1@example.com`)

### Display Name Auto-Generation
- If display name is empty, it will be auto-generated from first and last names
- Format: `"First Last"` or just the available name if only one is provided

### Duplicate Handling
- **Update Existing**: If checked, existing recipients (matched by email) will be updated with new information
- **Skip Existing**: If unchecked (default), existing recipients will be skipped

### Validation Rules
- At least one of first name or last name must be provided
- Empty rows are automatically skipped
- Invalid data will be reported with specific row numbers

## Import Process

1. **Upload File**: Select your CSV or Excel file
2. **Choose Options**: Decide whether to update existing recipients
3. **Click Import**: The system will process the file
4. **Review Results**: You'll see a summary of:
   - Number of recipients created
   - Number of recipients updated
   - Number of recipients skipped
   - Any errors encountered

## Error Handling

The system provides detailed error messages including:
- Missing required columns
- Invalid file formats
- Row-specific errors with line numbers
- File size or parsing errors

## Best Practices

1. **Test with Small Files**: Start with a small sample file to verify the format
2. **Backup Data**: Consider exporting existing recipients before large imports
3. **Clean Data**: Ensure your data is clean and properly formatted
4. **Check Results**: Always review the import summary for any issues
5. **Use Update Option Carefully**: Only check "Update existing" if you want to modify existing recipient data

## Database Fields Mapping

| File Column | Database Field | Description |
|-------------|----------------|-------------|
| Display name | `name` | Full display name |
| First name | `first_name` | Given name |
| Last name | `last_name` | Family name |
| Email | `email` | Email address (unique) |

## Technical Notes

- The import process uses database transactions for data integrity
- File processing is done in memory using pandas
- All operations are logged for audit purposes
- The feature requires pandas and openpyxl packages to be installed

## Troubleshooting

### Common Issues

1. **"Missing required columns" error**
   - Ensure your file has the exact headers: "Display name", "First name", "Last name"
   - Headers are case-insensitive but must match exactly

2. **"File size too large" error**
   - Files must be under 10MB
   - Consider splitting large files into smaller chunks

3. **"Cannot generate email" errors**
   - Ensure each row has at least a first name or last name
   - Or provide email addresses directly

4. **Encoding issues with CSV files**
   - Save CSV files with UTF-8 encoding
   - Avoid special characters in file names

### Getting Help

If you encounter issues:
1. Check the error messages for specific guidance
2. Verify your file format matches the examples
3. Test with the provided sample files
4. Contact your system administrator for technical support

## Sample Files

Sample files are available in the project directory:
- `sample_recipients.csv` - CSV format example
- `sample_recipients.xlsx` - Excel format example

You can use these files to test the bulk import functionality.
