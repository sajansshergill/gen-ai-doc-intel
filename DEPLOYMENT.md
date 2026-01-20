# 🚀 Complete Deployment Guide

## ✅ Current Status

- ✅ **Frontend**: Deployed at https://sajansshergill.github.io/gen-ai-doc-intel/
- ⏳ **Backend**: Ready to deploy to Render (see below)

## Part 1: Deploy Backend API to Render

### Quick Deploy to Render (Free Tier)

1. **Sign up**: https://render.com (free tier available)

2. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect GitHub repo: `sajansshergill/gen-ai-doc-intel`
   - Settings (auto-filled from `render.yaml`):
     - **Name**: `gen-ai-doc-intel-api` (or your choice)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Free
   - Click "Create Web Service"

3. **Configure Environment Variables** (in Render Dashboard):
   - `PYTHON_VERSION` = `3.11`
   - `LLM_PROVIDER` = `openai`
   - Optional (if using LLMs):
     - `OPENAI_API_KEY` = your OpenAI API key
     - `GEMINI_API_KEY` = your Gemini API key

4. **Wait 5-10 minutes** for deployment

5. **Copy your backend URL** (e.g., `https://gen-ai-doc-intel-api.onrender.com`)

### Important: Render Free Tier Notes

- ⚠️ **Cold Starts**: Free tier sleeps after 15min inactivity. First request takes ~30s to wake up.
- ⚠️ **Memory Limit**: 512MB RAM (already optimized in code)
- ⚠️ **Request Timeout**: 30 seconds (uploads return immediately, processing happens in background)

### Configure Frontend

1. Go to: https://github.com/sajansshergill/gen-ai-doc-intel/settings/secrets/actions
2. Add/Update secret: `API_BASE_URL` = your Render URL (e.g., `https://gen-ai-doc-intel-api.onrender.com`)
3. Re-run GitHub Pages workflow:
   - Go to: https://github.com/sajansshergill/gen-ai-doc-intel/actions
   - Click "Deploy to GitHub Pages" → "Run workflow"

## Part 2: Frontend Already Deployed ✅

Frontend is live at: https://sajansshergill.github.io/gen-ai-doc-intel/

## Testing

- **Backend API Docs**: `https://your-render-url.onrender.com/docs`
- **Health Check**: `https://your-render-url.onrender.com/health`
- **Test Upload**: `curl -X POST https://your-render-url.onrender.com/v1/test-upload`
- **Frontend**: https://sajansshergill.github.io/gen-ai-doc-intel/

## Troubleshooting Upload Issues

### Upload Failed? Try These Steps:

1. **Check Render Logs**:
   - Go to Render Dashboard → Your Service → Logs
   - Look for `[UPLOAD ERROR]` messages
   - Check for memory errors or timeout messages

2. **Verify File Size**:
   - Maximum file size: 10MB
   - Try with a smaller file first (1-2MB)

3. **Test Backend Connectivity**:
   ```bash
   # Test health endpoint
   curl https://your-render-url.onrender.com/health
   
   # Test upload endpoint
   curl -X POST https://your-render-url.onrender.com/v1/test-upload
   ```

4. **Check CORS Configuration**:
   - Backend already configured for GitHub Pages
   - If issues persist, check browser console for CORS errors

5. **Wait for Cold Start**:
   - If backend was sleeping, wait ~30 seconds after first request
   - Try uploading again

6. **Check Memory Usage**:
   - Render Dashboard → Metrics
   - If memory is consistently high, try smaller files

### Common Issues

- **"Upload Failed" immediately**: 
  - Backend might be sleeping (cold start)
  - Check Render logs for errors
  - Verify `API_BASE_URL` secret is correct

- **Backend spins down**: 
  - Free tier sleeps after 15min inactivity
  - First request takes ~30s to wake up
  - This is normal for free tier

- **Memory errors**: 
  - Already optimized for 512MB limit
  - Try smaller files if issues persist
  - Check logs for specific memory errors

- **CORS errors**: 
  - Backend already configured for GitHub Pages
  - Verify backend URL is correct in GitHub secret

- **404 errors**: 
  - Wait 2-3 minutes for GitHub Pages to propagate changes
  - Clear browser cache

## Render Configuration

The `render.yaml` file automatically configures:
- Python 3.11 environment
- Build and start commands
- Environment variables

You can also configure these manually in Render Dashboard if needed.

## Next Steps After Deployment

1. ✅ Deploy backend to Render
2. ✅ Update GitHub secret `API_BASE_URL`
3. ✅ Re-run GitHub Pages workflow
4. ✅ Test uploads on frontend
5. ✅ Check Render logs if issues occur
