# 🚀 Complete Deployment Guide

## ✅ Current Status

- ✅ **Frontend**: Deployed at https://sajansshergill.github.io/gen-ai-doc-intel/
- ⏳ **Backend**: Ready to deploy (see below)

## Part 1: Deploy Backend API (Required)

### Quick Deploy to Render (Free Tier)

1. **Sign up**: https://render.com (free tier)
2. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect GitHub repo: `sajansshergill/gen-ai-doc-intel`
   - Settings (auto-filled from `render.yaml`):
     - Build: `pip install -r requirements.txt`
     - Start: `uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`
   - Click "Create Web Service"
3. **Wait 5-10 minutes** for deployment
4. **Copy your backend URL** (e.g., `https://gen-ai-doc-intel-api.onrender.com`)

### Configure Frontend

1. Go to: https://github.com/sajansshergill/gen-ai-doc-intel/settings/secrets/actions
2. Add secret: `API_BASE_URL` = your Render URL
3. Re-run GitHub Pages workflow

## Part 2: Frontend Already Deployed ✅

Frontend is live at: https://sajansshergill.github.io/gen-ai-doc-intel/

## Testing

- **Backend API Docs**: `https://your-backend-url.onrender.com/docs`
- **Frontend**: https://sajansshergill.github.io/gen-ai-doc-intel/

## Troubleshooting

- **Backend spins down?** Free tier sleeps after 15min. First request takes ~30s.
- **CORS errors?** Backend already configured for GitHub Pages.
- **404 errors?** Wait 2-3 minutes for GitHub to propagate changes.
