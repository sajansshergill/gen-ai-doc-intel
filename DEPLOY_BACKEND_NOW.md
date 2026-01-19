# 🚀 Deploy Backend API to Render - Step by Step

## ✅ Prerequisites Ready!
- ✅ Deployment config files created (`render.yaml`, `Procfile`, `runtime.txt`)
- ✅ Code pushed to GitHub
- ✅ CORS configured for GitHub Pages

## 📋 Step-by-Step Deployment

### Step 1: Sign Up for Render (Free Tier)

1. Go to: **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with your GitHub account (recommended) or email
4. Verify your email if needed

### Step 2: Create New Web Service

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already connected
3. Select repository: **`sajansshergill/gen-ai-doc-intel`**
4. Click **"Connect"**

### Step 3: Configure Service Settings

Fill in the form:

- **Name**: `gen-ai-doc-intel-api` (or any name you prefer)
- **Environment**: Select **"Python 3"**
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: Leave empty (uses root)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`

**OR** if `render.yaml` is detected, Render will auto-fill these settings!

### Step 4: Set Environment Variables (Optional)

Click **"Advanced"** → **"Add Environment Variable"**:

- **OPENAI_API_KEY**: `your-openai-api-key` (if you have one)
- **GEMINI_API_KEY**: `your-gemini-api-key` (if you have one)
- **LLM_PROVIDER**: `openai` (or `gemini`)

**Note**: These are optional. The API will work without them, but LLM features won't work.

### Step 5: Deploy!

1. Scroll down and click **"Create Web Service"**
2. Render will start building and deploying
3. Wait 5-10 minutes for first deployment
4. You'll see build logs in real-time

### Step 6: Get Your Backend URL

Once deployment completes:
- Your backend URL will be: `https://gen-ai-doc-intel-api.onrender.com` (or similar)
- Copy this URL!

### Step 7: Configure Frontend to Use Backend

1. Go to: **https://github.com/sajansshergill/gen-ai-doc-intel/settings/secrets/actions**
2. Click **"New repository secret"**
3. **Name**: `API_BASE_URL`
4. **Value**: Your Render URL (e.g., `https://gen-ai-doc-intel-api.onrender.com`)
5. Click **"Add secret"**

### Step 8: Re-deploy Frontend

1. Go to: **https://github.com/sajansshergill/gen-ai-doc-intel/actions**
2. Click **"Deploy to GitHub Pages"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait for deployment to complete

### Step 9: Test!

1. Visit: **https://sajansshergill.github.io/gen-ai-doc-intel/**
2. Try uploading a document
3. Try querying documents
4. Everything should work! 🎉

## 🔍 Verify Backend is Working

Test your backend API:

```bash
# Health check
curl https://your-backend-url.onrender.com/

# API docs
# Visit: https://your-backend-url.onrender.com/docs
```

## ⚠️ Important Notes

### Free Tier Limitations:
- **Spins down after 15 minutes of inactivity**
- First request after spin-down takes ~30 seconds (cold start)
- **512 MB RAM** limit
- **0.1 CPU** limit

### To Keep Service Active:
- Render Pro plan ($7/month) keeps services always on
- Or use a monitoring service to ping your API every 10 minutes

### If Deployment Fails:
1. Check build logs in Render dashboard
2. Common issues:
   - Missing system dependencies (Tesseract, Poppler) - already handled in Dockerfile
   - Python version mismatch - set in `runtime.txt`
   - Port binding - handled by `$PORT` variable

## 🎯 Quick Reference

- **Backend URL**: `https://gen-ai-doc-intel-api.onrender.com` (your actual URL)
- **Frontend URL**: `https://sajansshergill.github.io/gen-ai-doc-intel/`
- **API Docs**: `https://your-backend-url.onrender.com/docs`
- **Render Dashboard**: https://dashboard.render.com

## 🆘 Troubleshooting

### Backend not responding?
- Check Render dashboard for service status
- Check logs for errors
- Verify environment variables are set correctly

### CORS errors?
- Backend already configured to allow all origins
- Check browser console for specific error

### Frontend still shows errors?
- Verify `API_BASE_URL` secret is set correctly
- Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Check browser console for errors

## ✅ Success Checklist

- [ ] Render account created
- [ ] Web service created and deployed
- [ ] Backend URL obtained
- [ ] `API_BASE_URL` secret set in GitHub
- [ ] Frontend re-deployed
- [ ] Tested document upload
- [ ] Tested query functionality

## 🎉 You're Done!

Your full-stack GenAI Document Intelligence Platform is now deployed!
