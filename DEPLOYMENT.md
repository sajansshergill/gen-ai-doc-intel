# Deployment Guide

This guide covers deploying both the frontend (GitHub Pages) and backend (FastAPI) components of the GenAI Document Intelligence Platform.

## Architecture

- **Frontend**: Static HTML/CSS/JS → GitHub Pages
- **Backend**: FastAPI Python API → Cloud Platform (Render, Railway, Fly.io, etc.)

## Part 1: Deploy Frontend to GitHub Pages

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. Save the settings

### Step 2: Set API URL Secret (Optional)

If your backend is deployed, set the API URL:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `API_BASE_URL`
4. Value: Your backend URL (e.g., `https://your-app.onrender.com`)
5. Click **Add secret**

If you don't set this, the frontend will try to use the same origin (which won't work for GitHub Pages).

### Step 3: Push to GitHub

The GitHub Actions workflow will automatically deploy when you push to `main`:

```bash
git add .
git commit -m "Setup GitHub Pages deployment"
git push origin main
```

### Step 4: Verify Deployment

1. Go to **Actions** tab in your GitHub repository
2. Wait for the "Deploy to GitHub Pages" workflow to complete
3. Your site will be available at: `https://YOUR_USERNAME.github.io/gen-ai-doc-intel/`

## Part 2: Deploy Backend API

### Option A: Render (Recommended - Free Tier Available)

1. **Create Account**: Sign up at [render.com](https://render.com)

2. **Create New Web Service**:
   - Connect your GitHub repository
   - Name: `gen-ai-doc-intel-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**:
   ```
   OPENAI_API_KEY=your-key-here (optional)
   GEMINI_API_KEY=your-key-here (optional)
   LLM_PROVIDER=openai (or gemini)
   ```

4. **Deploy**: Click "Create Web Service"

5. **Update Frontend**: Copy your Render URL and set it as `API_BASE_URL` secret in GitHub

### Option B: Railway

1. **Install Railway CLI**: `npm i -g @railway/cli`
2. **Login**: `railway login`
3. **Initialize**: `railway init`
4. **Deploy**: `railway up`
5. **Set Environment Variables**: Use Railway dashboard
6. **Get URL**: Railway provides a URL automatically

### Option C: Fly.io

1. **Install Fly CLI**: 
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**: `fly auth login`

3. **Create App**: `fly launch`

4. **Deploy**: `fly deploy`

5. **Get URL**: `fly info` shows your app URL

### Option D: Heroku

1. **Install Heroku CLI**: [heroku.com/cli](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login**: `heroku login`

3. **Create App**: `heroku create gen-ai-doc-intel-api`

4. **Set Buildpacks**:
   ```bash
   heroku buildpacks:set heroku/python
   ```

5. **Set Environment Variables**:
   ```bash
   heroku config:set OPENAI_API_KEY=your-key
   ```

6. **Deploy**: `git push heroku main`

## Part 3: Update Frontend API URL

After deploying the backend:

1. Go to GitHub repository → **Settings** → **Secrets** → **Actions**
2. Add/Update `API_BASE_URL` secret with your backend URL
3. Re-run the GitHub Actions workflow or push a new commit

## Part 4: CORS Configuration

If you encounter CORS errors, update `apps/api/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://YOUR_USERNAME.github.io", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing Locally

Before deploying, test the setup:

1. **Start Backend**:
   ```bash
   uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
   ```

2. **Test Frontend Locally**:
   ```bash
   cd apps/web/static
   python -m http.server 8080
   ```

3. **Set API URL**: Open browser console and run:
   ```javascript
   window.API_BASE_URL = 'http://localhost:8000';
   location.reload();
   ```

## Troubleshooting

### Frontend can't connect to API
- Check `API_BASE_URL` secret is set correctly
- Verify backend is running and accessible
- Check browser console for CORS errors
- Ensure backend CORS middleware allows GitHub Pages origin

### GitHub Pages shows 404
- Check GitHub Actions workflow completed successfully
- Verify `index.html` is in the root of `_site` directory
- Check repository Settings → Pages shows correct URL

### Backend deployment fails
- Check build logs for missing dependencies
- Verify `requirements.txt` includes all packages
- Ensure Python version matches (3.8+)
- Check environment variables are set correctly

## Quick Reference

- **Frontend URL**: `https://YOUR_USERNAME.github.io/gen-ai-doc-intel/`
- **Backend URL**: Depends on deployment platform
- **API Docs**: `https://YOUR_BACKEND_URL/docs`
- **ReDoc**: `https://YOUR_BACKEND_URL/redoc`
