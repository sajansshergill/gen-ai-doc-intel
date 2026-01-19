# Quick Setup: GitHub Pages Deployment

## Step-by-Step Guide

### 1. Push Code to GitHub

If you haven't already, push your code:

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/gen-ai-doc-intel.git

# Push to GitHub
git push -u origin main
```

### 2. Enable GitHub Pages

1. Go to your repository on GitHub: `https://github.com/YOUR_USERNAME/gen-ai-doc-intel`
2. Click **Settings** (top menu)
3. Scroll down to **Pages** (left sidebar)
4. Under **Source**, select **GitHub Actions**
5. Click **Save**

### 3. Wait for Deployment

1. Go to the **Actions** tab in your repository
2. You should see "Deploy to GitHub Pages" workflow running
3. Wait for it to complete (green checkmark)
4. Your site will be live at: `https://YOUR_USERNAME.github.io/gen-ai-doc-intel/`

### 4. (Optional) Set Backend API URL

If you've deployed the backend API:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `API_BASE_URL`
4. Value: Your backend URL (e.g., `https://your-app.onrender.com`)
5. Click **Add secret**
6. Re-run the workflow or push a new commit

### 5. Test Your Deployment

Visit: `https://YOUR_USERNAME.github.io/gen-ai-doc-intel/`

You should see the GenAI Document Intelligence Platform UI!

## Troubleshooting

**Workflow fails?**
- Check the Actions tab for error messages
- Ensure all files are committed and pushed
- Verify `.github/workflows/deploy-pages.yml` exists

**Page shows 404?**
- Wait a few minutes for GitHub to propagate changes
- Check Settings → Pages shows the correct URL
- Verify the workflow completed successfully

**Frontend can't connect to API?**
- Set the `API_BASE_URL` secret (see step 4 above)
- Or deploy the backend first (see DEPLOYMENT.md)
- Check browser console for errors

## Next Steps

- Deploy the backend API (see `DEPLOYMENT.md`)
- Update `API_BASE_URL` secret with your backend URL
- Customize the UI if needed
