# ORCID Publications Integration - Setup Guide

This guide explains how to set up automatic publication syncing from your ORCID profile to your GitHub Pages site.

## 🔐 Security Notice

**IMPORTANT**: Your ORCID credentials are stored as GitHub Secrets and are NEVER committed to the repository. The workflow uses environment variables to securely access these credentials.

## 📋 Prerequisites

You already have:
- ✅ ORCID API credentials (Client ID and Client Secret)
- ✅ ORCID account with publications

## 🚀 Setup Instructions

### Step 1: Add GitHub Secrets

1. Go to your GitHub repository: https://github.com/sorujov/sorujov.github.io

2. Click **Settings** (top menu)

3. In the left sidebar, click **Secrets and variables** → **Actions**

4. Click **New repository secret** button

5. Add THREE secrets with these exact names:

   **Secret 1:**
   - Name: `ORCID_ID`
   - Value: Your ORCID ID (e.g., `0009-0004-9708-2109`)
   
   **Secret 2:**
   - Name: `ORCID_CLIENT_ID`
   - Value: `APP-47UE3N9TJQ6WG0R2`
   
   **Secret 3:**
   - Name: `ORCID_CLIENT_SECRET`
   - Value: `8ac081a7-ddab-43d7-8916-d458e6180b80`

### Step 2: Enable GitHub Actions

1. Go to the **Actions** tab in your repository

2. If prompted, click **Enable workflows**

3. You should see the workflow: "Update ORCID Publications"

### Step 3: Run the Workflow Manually (First Time)

1. In the **Actions** tab, click on "Update ORCID Publications"

2. Click **Run workflow** button (top right)

3. Select `master` branch

4. Click **Run workflow**

5. Wait for the workflow to complete (usually 30-60 seconds)

6. Check the workflow results to see how many publications were imported

### Step 4: Verify the Import

1. Go to your repository and check the `_publications/` folder

2. You should see new markdown files for each publication from your ORCID profile

3. Visit your website: https://sorujov.github.io/publications/

4. Publications should be displayed in two categories:
   - **Published Works** (journal articles, conference papers, books)
   - **Working Papers** (working papers, preprints, reports)

## 🔄 Automatic Updates

The workflow will automatically run:
- **Every Monday at midnight UTC** (weekly sync)
- **Manually** when you trigger it from the Actions tab
- **Automatically** when you push changes to the workflow file

## 📝 Customizing Publications

After the initial import, you can edit the generated markdown files in `_publications/` to:
- Add detailed abstracts
- Include additional information
- Add custom formatting
- Link to supplementary materials

**Note**: Manual edits will be preserved during future ORCID syncs as long as you don't change the filename.

## 🏷️ Publication Categories

Publications are automatically categorized based on their type in ORCID:

| ORCID Type | Category | Display Section |
|-----------|----------|-----------------|
| `journal-article` | manuscripts | Published Works |
| `conference-paper` | manuscripts | Published Works |
| `book-chapter` | manuscripts | Published Works |
| `book` | manuscripts | Published Works |
| `working-paper` | working-papers | Working Papers |
| `preprint` | working-papers | Working Papers |
| `report` | working-papers | Working Papers |

## 🛠️ Troubleshooting

### Workflow Fails with "ORCID_ID not set"
- Verify that you added all three secrets with the exact names shown above
- Secrets are case-sensitive

### No Publications Appear
- Check your ORCID profile to ensure publications are listed
- Verify your ORCID ID is correct in the secret
- Check the workflow logs in the Actions tab for error messages

### Authentication Errors
- Verify your Client ID and Client Secret are correct
- Ensure there are no extra spaces in the secret values
- Try regenerating your ORCID API credentials

### Publications Not Updating
- The workflow runs weekly by default
- Manually trigger it from the Actions tab to force an update
- Check if there are new publications in your ORCID profile

## 📂 File Structure

```
sorujov.github.io/
├── .github/
│   └── workflows/
│       └── update-orcid-publications.yml    # GitHub Actions workflow
├── scripts/
│   └── fetch_orcid_publications.py          # Python script to fetch from ORCID
├── _publications/                            # Generated markdown files
│   └── YYYY-MM-DD-publication-title.md
└── _pages/
    └── publications.html                     # Publications page layout
```

## 🔗 Resources

- **ORCID API Documentation**: https://info.orcid.org/documentation/api-tutorials/
- **Your ORCID Profile**: https://orcid.org/0009-0004-9708-2109
- **GitHub Actions Logs**: https://github.com/sorujov/sorujov.github.io/actions

## 📧 Support

If you encounter any issues, check the GitHub Actions logs for detailed error messages. The workflow provides comprehensive error reporting and summaries.

---

**Last Updated**: December 2025
**Version**: 1.0
