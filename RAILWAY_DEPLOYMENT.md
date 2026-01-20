# 🚂 Railway Deployment Guide

Railway is a better alternative to Render for Python/FastAPI apps. It has:
- ✅ Better free tier (512MB RAM, more reliable)
- ✅ No cold starts (stays awake)
- ✅ Better file upload handling
- ✅ Simpler deployment
- ✅ Better logging

## Step 1: Sign Up for Railway

1. Go to: https://railway.app
2. Sign up with GitHub (free tier available)
3. Click "New Project" → "Deploy from GitHub repo"

## Step 2: Connect Repository

1. Select your repository: `sajansshergill/gen-ai-doc-intel`
2. Railway will auto-detect Python and use `railway.json`
3. Click "Deploy Now"

## Step 3: Configure Environment Variables

In Railway dashboard → Variables tab, add:

```
PYTHON_VERSION=3.11
LLM_PROVIDER=openai
```

Optional (if using LLMs):
```
OPENAI_API_KEY=your-key-here
GEMINI_API_KEY=your-key-here
```

## Step 4: Get Your Railway URL

1. After deployment (2-3 minutes), Railway will provide a URL like:
   - `https://gen-ai-doc-intel-production.up.railway.app`
2. Copy this URL

## Step 5: Update Frontend Configuration

1. Go to: https://github.com/sajansshergill/gen-ai-doc-intel/settings/secrets/actions
2. Update secret: `API_BASE_URL` = your Railway URL
3. Re-run GitHub Pages workflow

## Step 6: Test Deployment

- **Backend Health**: `https://your-railway-url.up.railway.app/health`
- **API Docs**: `https://your-railway-url.up.railway.app/docs`
- **Frontend**: https://sajansshergill.github.io/gen-ai-doc-intel/

## Troubleshooting

### Upload Still Failing?

1. **Check Railway Logs**:
   - Railway Dashboard → Deployments → View Logs
   - Look for `[UPLOAD ERROR]` messages

2. **Common Issues**:
   - File too large (>10MB) → Reduce file size
   - Memory limit → Already optimized, should work
   - Directory permissions → Already handled in code

3. **Test Upload Endpoint**:
   ```bash
   curl -X POST https://your-railway-url.up.railway.app/v1/test-upload
   ```

### Railway vs Render

| Feature | Railway | Render |
|---------|---------|--------|
| Free Tier RAM | 512MB | 512MB |
| Cold Starts | No | Yes (15min) |
| File Uploads | ✅ Better | ⚠️ Issues |
| Logging | ✅ Excellent | ⚠️ Basic |
| Setup | ✅ Simple | ⚠️ Complex |

## Next Steps

1. Deploy to Railway (5 minutes)
2. Update GitHub secret with Railway URL
3. Test uploads - should work now! 🎉
