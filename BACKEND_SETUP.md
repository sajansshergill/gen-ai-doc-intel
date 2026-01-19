# 🔧 Backend API Setup Guide

## Current Status

✅ **Frontend is deployed** at: https://sajansshergill.github.io/gen-ai-doc-intel/  
❌ **Backend API is not deployed** - This is why you see errors

## Quick Fix Options

### Option 1: Deploy Backend to Render (Recommended - Free)

1. **Sign up**: https://render.com (free tier available)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect GitHub repository: `sajansshergill/gen-ai-doc-intel`
   - Name: `gen-ai-doc-intel-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`
   - Click "Create Web Service"

3. **Set Environment Variables** (optional):
   ```
   OPENAI_API_KEY=your-key-here
   GEMINI_API_KEY=your-key-here
   LLM_PROVIDER=openai
   ```

4. **Get Your Backend URL**:
   - After deployment, Render gives you a URL like: `https://gen-ai-doc-intel-api.onrender.com`

5. **Configure Frontend**:
   - Go to: https://github.com/sajansshergill/gen-ai-doc-intel/settings/secrets/actions
   - Click "New repository secret"
   - Name: `API_BASE_URL`
   - Value: Your Render URL (e.g., `https://gen-ai-doc-intel-api.onrender.com`)
   - Click "Add secret"
   - Re-run the GitHub Pages workflow

### Option 2: Deploy Backend to Railway

1. **Install Railway CLI**: `npm i -g @railway/cli`
2. **Login**: `railway login`
3. **Initialize**: `railway init`
4. **Deploy**: `railway up`
5. **Get URL**: Railway provides URL automatically
6. **Set API_BASE_URL secret** in GitHub (same as Option 1, step 5)

### Option 3: Run Backend Locally (For Testing)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start backend**:
   ```bash
   uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
   ```

3. **Update frontend config**:
   - Open browser console on GitHub Pages site
   - Run: `window.API_BASE_URL = 'http://localhost:8000'; location.reload();`
   - Note: This only works if you use a CORS extension or disable CORS

## Verify Backend is Working

Once backend is deployed, test it:

```bash
# Health check
curl https://your-backend-url.com/

# List documents
curl https://your-backend-url.com/v1/documents

# API docs
# Visit: https://your-backend-url.com/docs
```

## Troubleshooting

### CORS Errors
Make sure backend CORS allows GitHub Pages origin:
- Backend already configured to allow `*.github.io` origins
- If issues persist, check `apps/api/main.py` CORS settings

### API Not Found (404)
- Verify backend URL is correct
- Check backend logs for errors
- Ensure backend is running and accessible

### Frontend Still Shows Errors
- Clear browser cache
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Check browser console for errors
- Verify `API_BASE_URL` secret is set correctly

## Next Steps

1. ✅ Deploy backend (choose one option above)
2. ✅ Set `API_BASE_URL` secret in GitHub
3. ✅ Re-run GitHub Pages workflow
4. ✅ Test the full application!

## Need Help?

- Check `DEPLOYMENT.md` for detailed deployment guide
- Check `DEPLOYMENT_FIX.md` for GitHub Pages troubleshooting
- Backend API docs: `https://your-backend-url.com/docs`
