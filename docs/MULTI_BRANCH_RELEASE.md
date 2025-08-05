# Multi-Branch Release Automation

This repository now includes automated release workflows that handle different types of branches with appropriate versioning strategies.

## Overview

The release automation consists of two main workflows:

1. **Main Branch Release** (`auto-release.yml`) - Handles stable releases from the `main` branch
2. **Branch Release Automation** (`branch-release.yml`) - Handles pre-releases from all other branches

## Workflow Structure

### Main Branch Release (auto-release.yml)

**Triggers:**
- Push to `main` branch
- Excludes workflow changes and markdown files

**Behavior:**
- Creates stable release versions (e.g., `v1.2.3`)
- Increments patch version automatically
- Creates GitHub releases (not pre-releases)
- Sends release emails to configured recipients
- Only runs for production-ready code

**Version Pattern:** `v{major}.{minor}.{patch}`

### Branch Release Automation (branch-release.yml)

**Triggers:**
- Push to: `develop`, `feature/**`, `hotfix/**`, `release/**`, `bugfix/**`
- Pull requests to: `main`, `develop`
- Excludes workflow changes and markdown files

**Branch-Specific Behavior:**

#### Develop Branch
- **Version Pattern:** `v{major}.{minor+1}.0-beta.{date}.{sha}`
- **Example:** `v1.3.0-beta.20250104.abc1234`
- **Purpose:** Beta releases for integration testing

#### Release Branches
- **Version Pattern:** `v{version}-rc.{count}` or `v{major}.{minor+1}.0-rc.1`
- **Example:** `v1.3.0-rc.1`, `v1.3.0-rc.2`
- **Purpose:** Release candidates for final testing

#### Feature Branches
- **Version Pattern:** `v{major}.{minor}.{patch+1}-alpha.{feature-name}.{sha}`
- **Example:** `v1.2.4-alpha.user-auth.abc1234`
- **Purpose:** Alpha releases for feature testing

#### Hotfix Branches
- **Version Pattern:** `v{major}.{minor}.{patch+1}-hotfix.{date}.{sha}`
- **Example:** `v1.2.4-hotfix.20250104.abc1234`
- **Purpose:** Emergency fixes testing

#### Bugfix Branches
- **Version Pattern:** `v{major}.{minor}.{patch+1}-alpha.{bugfix-name}.{sha}`
- **Example:** `v1.2.4-alpha.fix-email-bug.abc1234`
- **Purpose:** Bug fix testing

#### Pull Request Versions
- **Version Pattern:** `{base-pattern}-pr.{number}`
- **Example:** `v1.2.4-alpha.user-auth.abc1234-pr.123`
- **Purpose:** Draft releases for PR review
- **Note:** These are draft releases and tags are not pushed to remote

## Branch Naming Conventions

To ensure proper version generation, follow these naming conventions:

```
main                    # Stable releases
develop                 # Beta releases
release/1.3.0          # Release candidates
feature/user-auth      # Feature alpha releases
feature/email-templates
hotfix/security-fix    # Hotfix releases
bugfix/typo-fix       # Bugfix alpha releases
```

## Email Notifications

### Main Branch Releases
- Full detailed release emails
- Sent to: configured email recipients in secrets
- Subject: "🚀 New Release: Mailer Application - {version}"

### Pre-Releases (Other Branches)
- Pre-release notification emails
- Sent to: configured email recipients in secrets
- Subject: "🧪 Pre-Release Available: {version} from {branch}"
- **Note:** Not sent for PR drafts

## Required GitHub Secrets

Configure these secrets in your repository settings:

```
SMTP_SERVER         # SMTP server address
SMTP_PORT          # SMTP server port
SMTP_USERNAME      # SMTP username
SMTP_PASSWORD      # SMTP password
EMAIL_TO           # Recipient email address
EMAIL_FROM         # Sender email address
```

## GitHub Release Types

| Branch Type | Release Type | Prerelease | Draft | Tag Pushed |
|-------------|--------------|------------|-------|------------|
| main        | Release      | No         | No    | Yes        |
| develop     | Pre-release  | Yes        | No    | Yes        |
| release/*   | Pre-release  | Yes        | No    | Yes        |
| feature/*   | Pre-release  | Yes        | No    | Yes        |
| hotfix/*    | Pre-release  | Yes        | No    | Yes        |
| bugfix/*    | Pre-release  | Yes        | No    | Yes        |
| PR to main/develop | Pre-release | Yes   | Yes   | No         |

## Usage Examples

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/user-authentication
git push origin feature/user-authentication

# Each push creates: v1.2.4-alpha.user-authentication.{sha}
```

### 2. Release Preparation
```bash
# Create release branch
git checkout -b release/1.3.0
git push origin release/1.3.0

# Each push creates: v1.3.0-rc.{count}
```

### 3. Hotfix
```bash
# Create hotfix branch
git checkout -b hotfix/security-vulnerability
git push origin hotfix/security-vulnerability

# Each push creates: v1.2.4-hotfix.{date}.{sha}
```

### 4. Pull Request Testing
```bash
# Create PR from feature branch to main
# Automatically creates: v1.2.4-alpha.user-authentication.{sha}-pr.{number}
# This is a DRAFT release for review purposes
```

## Best Practices

1. **Use descriptive branch names** - They become part of the version identifier
2. **Keep branch names short** - Long names create unwieldy version strings
3. **Test pre-releases** - Always test pre-release versions before merging to main
4. **Review PR drafts** - Use draft releases to review changes before merging
5. **Clean up old releases** - Periodically clean up old pre-release versions

## Skipping Releases

The workflow will skip release creation for commits with messages starting with:
- `v{version}` (version tags)
- `Release`
- `Tag`
- `Merge` (merge commits)

## Troubleshooting

### Version Already Exists
If a version already exists, the main branch workflow will increment by an additional patch version.

### No Tags Found
If no existing tags are found:
- Main branch starts with `v1.0.0`
- Other branches start with `v0.1.0` as base

### Email Delivery Issues
- Email sending is set to `continue-on-error: true`
- Failed emails won't block the release process
- Check SMTP configuration in secrets

### Duplicate Versions
The system uses SHA and timestamps to ensure uniqueness for pre-releases, but stable releases on main must be manually managed if conflicts occur.

## Migration from Single Workflow

If upgrading from a single workflow system:
1. Existing tags will be respected and used as base versions
2. Main branch behavior remains the same
3. Other branches will now get automatic pre-release versions
4. No manual intervention required for existing repositories

## Monitoring

You can monitor the release workflows through:
- GitHub Actions tab in your repository
- Release notifications via email
- GitHub Releases page
- Git tags in your repository

The system provides comprehensive logging to help debug any version generation issues.
