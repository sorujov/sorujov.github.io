# ORCID Publications Sync - Quick Start

## What Was Set Up

✅ **Python script** ([scripts/fetch_orcid_publications.py](scripts/fetch_orcid_publications.py)) that fetches your publications from ORCID API
✅ **GitHub Actions workflow** ([.github/workflows/update-orcid-publications.yml](.github/workflows/update-orcid-publications.yml)) for automated weekly updates
✅ **Updated publications page** with auto-sync indicator
✅ **Publication categories** configured (Published Works & Working Papers)

## ⚡ Quick Setup (5 minutes)

### 1. Add Your ORCID ID to GitHub Secrets

Go to: https://github.com/sorujov/sorujov.github.io/settings/secrets/actions

Add these **3 secrets**:

```
Name: ORCID_ID
Value: 0009-0004-9708-2109
```

```
Name: ORCID_CLIENT_ID
Value: APP-47UE3N9TJQ6WG0R2
```

```
Name: ORCID_CLIENT_SECRET
Value: 8ac081a7-ddab-43d7-8916-d458e6180b80
```

### 2. Push These Changes to GitHub

```bash
git add .
git commit -m "Add ORCID publications automation"
git push origin master
```

### 3. Run the Workflow

Go to: https://github.com/sorujov/sorujov.github.io/actions

- Click "Update ORCID Publications"
- Click "Run workflow"
- Select branch: `master`
- Click "Run workflow" button

### 4. Check Your Publications Page

Visit: https://sorujov.github.io/publications/

Your publications from ORCID will be automatically displayed!

## 🔄 How It Works

- **Automatic**: Runs every Monday at midnight UTC
- **Manual**: Trigger anytime from GitHub Actions tab
- **Secure**: Credentials stored in GitHub Secrets (never in code)
- **Smart**: Only commits if new publications found
- **Categorized**: Separates published works from working papers

## 📝 Need More Details?

See [ORCID_SETUP_GUIDE.md](ORCID_SETUP_GUIDE.md) for complete documentation.

## 🎯 Benefits

✨ **No manual updates needed** - Your publications page stays current automatically
🔒 **Secure** - API credentials never exposed in code
📊 **Organized** - Publications automatically categorized by type
🚀 **Fast** - Updates complete in under 1 minute
✏️ **Customizable** - Edit generated files to add abstracts and details
