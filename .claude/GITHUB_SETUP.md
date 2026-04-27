# GitHub Repository Setup Guide

This document walks you through creating your GitHub repository for the Python `inundation` package.

## Step 1: Create a New Repository on GitHub

1. Go to [GitHub](https://github.com/new)
2. **Repository name:** `inundation`
3. **Description:** `Python package for calculating Yolo Bypass inundation duration`
4. **Visibility:** Public
5. **Initialize repository:** No (we'll push our files)
   - ❌ Don't add README (we have one)
   - ❌ Don't add .gitignore (we have one)
   - ❌ Don't add License (we have one)
6. Click **Create repository**

## Step 2: Push Your Local Code

Once created, you'll see instructions on the repo page. Follow these commands in your terminal:

```bash
# Navigate to your project directory
cd /path/to/inundation

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Python translation of inundation package"

# Add remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/inundation.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 3: Enable GitHub Features

### Enable Workflows
1. Go to **Settings** → **Actions**
2. Under "Actions permissions," select **Allow all actions and reusable workflows**
3. Click **Save**

### Enable Code Analysis (Optional but Recommended)
1. Go to **Settings** → **Security and analysis**
2. Enable:
   - ✅ **Dependabot alerts**
   - ✅ **Dependabot security updates** (auto-merge patches)
   - ✅ **Secret scanning** (if public repo)

### Add Branch Protection (Optional)
1. Go to **Settings** → **Branches**
2. Click **Add rule** under "Branch protection rules"
3. **Branch name pattern:** `main`
4. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require code reviews before merging (at least 1)

## Step 4: Update Files with Your GitHub Username

Before pushing, replace these placeholders:
- `YOUR-USERNAME` → Your actual GitHub username
- `[YOUR NAME]` → Your full name
- `your.email@example.com` → Your email
- `[YOUR AFFILIATION]` → Your institution/affiliation

### Files to update:
- `pyproject.toml` - lines 9, 21, 28-30, 37, 40
- `README.md` - multiple locations
- `CITATION.cff` - lines 10-12, 14-15
- `LICENSE` - line 3

### Quick replacements (in terminal):
```bash
# Replace YOUR-USERNAME
sed -i 's/YOUR-USERNAME/your-github-username/g' pyproject.toml README.md CITATION.cff

# Replace [YOUR NAME]
sed -i 's/\[YOUR NAME\]/Your Full Name/g' pyproject.toml CITATION.cff
sed -i 's/\[YOUR FIRST NAME\]/Your First Name/g' CITATION.cff
sed -i 's/\[YOUR AFFILIATION\]/UC Davis/g' CITATION.cff

# Replace email
sed -i 's/your.email@example.com/your-email@ucdavis.edu/g' pyproject.toml
```

## Step 5: Set Up Codecov (Optional)

For coverage reporting:

1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Click **Add a new repository**
4. Select your `inundation` repository
5. Follow the setup (nothing to add—we already have the action in CI)

## Step 6: Create a Develop Branch (Optional)

```bash
# Create develop branch
git checkout -b develop
git push -u origin develop
```

Then update `.github/workflows/ci.yml` if you want CI to run on both `main` and `develop` (we already have this configured).

## Step 7: Add Topics (Optional)

In your repo's **About** section (top right), add topics:
- `python`
- `hydrology`
- `california`
- `water-resources`
- `yolo-bypass`
- `inundation`

## Step 8: Create Initial Issues (Optional)

In the **Issues** tab, create a few issues for your team:

```markdown
### TODO: Complete Python Implementation

- [ ] Translate `get_fre()` function
- [ ] Translate `get_dayflow()` function
- [ ] Translate `calc_inundation()` function
- [ ] Write comprehensive test suite
- [ ] Create documentation
- [ ] Release v0.1.0 to PyPI
```

## Quick Checklist

- [ ] Repository created on GitHub
- [ ] Code pushed to `main` branch
- [ ] `pyproject.toml`, `README.md`, `CITATION.cff` updated with your info
- [ ] GitHub Actions enabled (Settings → Actions)
- [ ] Branch protection enabled (Settings → Branches)
- [ ] LICENSE file configured
- [ ] Topics added to repo
- [ ] README.md badges point to correct repo

## What's Next?

Once your repo is set up:

1. Start translating the R functions to Python
2. Each commit will trigger GitHub Actions (lint, type-check, test)
3. Monitor the Actions tab to ensure everything passes
4. Create pull requests for major changes (good practice)

## Need Help?

- [GitHub Docs: Creating a Repository](https://docs.github.com/en/get-started/quickstart/create-a-repo)
- [GitHub Docs: Pushing Code](https://docs.github.com/en/get-started/importing-your-projects-to-github/importing-a-git-repository-using-the-command-line)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)