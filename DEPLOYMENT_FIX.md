# 🔧 GitHub Pages Deployment - Complete Fix Guide

## ⚠️ Critical: Enable GitHub Pages First!

**The workflows are failing because GitHub Pages must be enabled BEFORE the workflow can run.**

### Step 1: Enable GitHub Pages (REQUIRED)

1. **Go to**: https://github.com/sajansshergill/gen-ai-doc-intel/settings/pages
2. **Under "Source"**, select **"GitHub Actions"** (NOT "Deploy from a branch")
3. **Click "Save"**

**This creates the `github-pages` environment that the workflow needs!**

### Step 2: Verify Workflow

After enabling Pages, the workflow will automatically run on the next push, or you can:

1. Go to: https://github.com/sajansshergill/gen-ai-doc-intel/actions
2. Click **"Deploy to GitHub Pages"**
3. Click **"Run workflow"** → **"Run workflow"**

### Step 3: Monitor Deployment

Watch the workflow run:
- **Yellow dot** = Running
- **Green checkmark** = Success ✅
- **Red X** = Failed (check logs)

## 🎯 What the Workflow Does

1. **Build Job**:
   - Copies static files from `apps/web/static/` to `_site/`
   - Fixes CSS/JS paths (removes `/static/` prefix)
   - Creates `config.js` for API URL configuration
   - Injects config script into `index.html`
   - Uploads artifact

2. **Deploy Job**:
   - Deploys the artifact to GitHub Pages
   - Makes site live at: `https://sajansshergill.github.io/gen-ai-doc-intel/`

## 🔍 Troubleshooting

### Workflow fails immediately (9-10 seconds)
**Cause**: GitHub Pages not enabled
**Fix**: Enable GitHub Pages in Settings → Pages → Source: "GitHub Actions"

### Workflow fails at "Deploy to GitHub Pages" step
**Cause**: `github-pages` environment doesn't exist
**Fix**: Enable GitHub Pages first (see Step 1)

### Workflow succeeds but site shows 404
**Cause**: GitHub needs time to propagate (2-5 minutes)
**Fix**: Wait a few minutes and refresh

### CSS/JS not loading
**Cause**: Path issues in HTML
**Fix**: Already handled in workflow - paths are fixed automatically

## ✅ Success Checklist

- [ ] GitHub Pages enabled in Settings → Pages
- [ ] Source set to "GitHub Actions"
- [ ] Workflow runs successfully (green checkmark)
- [ ] Site accessible at: https://sajansshergill.github.io/gen-ai-doc-intel/
- [ ] CSS and JavaScript load correctly
- [ ] No console errors in browser

## 📝 Optional: Set Backend API URL

If you deploy the backend API:

1. Go to: https://github.com/sajansshergill/gen-ai-doc-intel/settings/secrets/actions
2. Click **"New repository secret"**
3. Name: `API_BASE_URL`
4. Value: Your backend URL (e.g., `https://your-app.onrender.com`)
5. Click **"Add secret"**
6. Re-run the workflow

The `config.js` file will automatically use this URL.

## 🚀 Quick Deploy Command

After enabling GitHub Pages, trigger deployment:

```bash
git commit --allow-empty -m "Trigger GitHub Pages deployment"
git push
```

Or manually trigger in GitHub Actions tab.
