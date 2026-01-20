# 🔧 Upload Troubleshooting Guide

## If Upload Still Fails

### Step 1: Check Browser Console
1. Open your app: https://sajansshergill.github.io/gen-ai-doc-intel/
2. Press **F12** (or right-click → Inspect)
3. Go to **Console** tab
4. Try uploading a file
5. Look for error messages - they will show the exact problem

### Step 2: Check Network Tab
1. In browser DevTools, go to **Network** tab
2. Try uploading
3. Find the `/v1/documents` request
4. Click it and check:
   - **Status code** (should be 200)
   - **Response** (what the server returned)
   - **Request Headers** (check CORS)

### Step 3: Test Backend Directly
```bash
# Test health endpoint
curl https://gen-ai-doc-intel.onrender.com/health

# Test upload endpoint (should return CORS enabled)
curl -X POST https://gen-ai-doc-intel.onrender.com/v1/test-upload
```

### Step 4: Common Issues

#### Issue: "Failed to fetch" or "NetworkError"
**Cause**: Backend not reachable or CORS issue
**Fix**: 
- Check backend URL is correct in GitHub secrets
- Verify backend is running (check Render dashboard)
- Wait 30 seconds if backend just woke up (free tier cold start)

#### Issue: "Upload failed: 500 Internal Server Error"
**Cause**: Backend processing error
**Fix**: 
- Check Render logs for error details
- File might be too large (>10MB)
- Processing might be failing silently

#### Issue: "Upload failed: 400 Bad Request"
**Cause**: Invalid file type or missing filename
**Fix**: 
- Use PDF, PNG, JPG, or TIFF files only
- Make sure file has a proper extension

#### Issue: Upload succeeds but no documents show
**Cause**: Processing failed in background
**Fix**: 
- Check Render logs
- Processing happens in background - wait a few seconds
- Refresh document list

### Step 5: Check Render Logs
1. Go to Render dashboard
2. Click on your service
3. Go to **Logs** tab
4. Look for errors when you upload

### Step 6: Verify Configuration
1. **Frontend API URL**: Check browser console for `API_BASE` value
2. **GitHub Secret**: Verify `API_BASE_URL` is set correctly
3. **Backend Status**: Check Render dashboard - should be "Live"

## Quick Test

Try this in browser console (F12):
```javascript
// Check API URL
console.log('API_BASE:', window.API_BASE_URL || window.location.origin);

// Test connection
fetch('https://gen-ai-doc-intel.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

## Still Not Working?

Share:
1. Browser console errors (screenshot or copy text)
2. Network tab details (status code, response)
3. Render logs (any errors)
4. File type and size you're trying to upload
