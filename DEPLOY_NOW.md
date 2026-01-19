# 🚀 Deploy to GitHub Pages - Quick Start

## ✅ Prerequisites (Already Done!)
- ✅ Code pushed to GitHub
- ✅ GitHub Actions workflow configured
- ✅ Repository: https://github.com/sajansshergill/gen-ai-doc-intel

## 🎯 3 Simple Steps

### Step 1: Enable GitHub Pages (1 minute)
1. **Click this link**: https://github.com/sajansshergill/gen-ai-doc-intel/settings/pages
2. Under **"Source"**, select **"GitHub Actions"**
3. Click **"Save"**

### Step 2: Trigger Deployment (30 seconds)
**Option A - Automatic**: Just push any commit (already done!)
```bash
git commit --allow-empty -m "Trigger GitHub Pages deployment"
git push
```

**Option B - Manual**: 
1. Go to: https://github.com/sajansshergill/gen-ai-doc-intel/actions
2. Click **"Deploy to GitHub Pages"** workflow
3. Click **"Run workflow"** → **"Run workflow"**

### Step 3: Wait & Access (2-3 minutes)
1. Go to: https://github.com/sajansshergill/gen-ai-doc-intel/actions
2. Wait for workflow to complete (green ✅)
3. Visit: **https://sajansshergill.github.io/gen-ai-doc-intel/**

## 🎉 That's It!

Your GenAI Document Intelligence Platform will be live!

## 📝 Optional: Connect Backend API

If you deploy the backend API (see `DEPLOYMENT.md`):

1. Go to: https://github.com/sajansshergill/gen-ai-doc-intel/settings/secrets/actions
2. Click **"New repository secret"**
3. Name: `API_BASE_URL`
4. Value: Your backend URL (e.g., `https://your-app.onrender.com`)
5. Click **"Add secret"**
6. Re-run the workflow

## 🔍 Troubleshooting

**Workflow not showing?**
- Make sure you enabled GitHub Actions in repository settings
- Check that `.github/workflows/deploy-pages.yml` exists

**404 Error?**
- Wait 2-3 minutes for GitHub to propagate
- Check Actions tab - workflow must complete successfully
- Verify Settings → Pages shows correct URL

**Need help?**
- Check `GITHUB_PAGES_SETUP.md` for detailed guide
- Check `DEPLOYMENT.md` for backend deployment
