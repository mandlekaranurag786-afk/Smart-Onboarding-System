# 🐛 Debug Chat Send Button Issue

## Steps to Debug

### 1. Open Browser Console
- Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
- Press `Cmd+Option+I` (Mac)
- Go to "Console" tab

### 2. Refresh the Page
```
Ctrl+R (Windows/Linux) or Cmd+R (Mac)
```

### 3. Try Sending a Message

Type in the chat: "What is the password policy?"

Click the Send button

### 4. Check Console Logs

You should see logs like:
```
[RAG Chat] Button clicked
[RAG Chat] Submit triggered, input: What is the password policy?
[RAG Chat] Adding user message: {...}
[RAG Chat] Calling API: http://localhost:8000/api/rag/query
[RAG Chat] Response status: 200
[RAG Chat] Response data: {...}
[RAG Chat] Adding bot message
[RAG Chat] Request complete
```

### 5. Common Issues

#### Issue 1: No logs appear
**Problem**: Button click not registering
**Fix**: 
- Check if button is disabled (should be blue, not gray)
- Make sure input field has text
- Try clicking suggested question buttons first

#### Issue 2: "Button clicked" but no "Submit triggered"
**Problem**: Form submission blocked
**Fix**: 
- Check browser console for errors
- Try pressing Enter key instead of clicking button

#### Issue 3: "CORS error" in console
**Problem**: Backend CORS not allowing frontend
**Fix**:
```bash
# Check backend CORS settings
# Should allow http://localhost:3000
```

#### Issue 4: "Failed to fetch" or "Network error"
**Problem**: Backend not running or wrong URL
**Fix**:
```bash
# Check backend is running
curl http://localhost:8000/health

# Check RAG endpoint
curl http://localhost:8000/api/rag/health
```

#### Issue 5: "API Error: 500"
**Problem**: Backend error
**Fix**:
```bash
# Check backend terminal for errors
# Make sure documents are indexed
cd backend
python init_rag.py
```

### 6. Manual API Test

Test the API directly from console:

```javascript
// Paste this in browser console
fetch('http://localhost:8000/api/rag/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'What is the password policy?',
    top_k: 5,
    include_sources: true
  })
})
.then(r => r.json())
.then(d => console.log('API Response:', d))
.catch(e => console.error('API Error:', e));
```

### 7. Check Network Tab

1. Open DevTools → Network tab
2. Click send button
3. Look for request to `/api/rag/query`
4. Check:
   - Status code (should be 200)
   - Response body
   - Request payload

### 8. Verify Environment

Check `.env.local` in frontend:
```bash
cat frontend/.env.local
```

Should show:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 9. Quick Fixes

#### Fix 1: Clear Browser Cache
```
Ctrl+Shift+Delete (Windows/Linux)
Cmd+Shift+Delete (Mac)
```

#### Fix 2: Hard Refresh
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

#### Fix 3: Restart Frontend
```bash
cd frontend
# Stop with Ctrl+C
npm run dev
```

#### Fix 4: Restart Backend
```bash
cd backend
# Stop with Ctrl+C
python -m uvicorn app.main:app --reload --port 8000
```

### 10. Expected Behavior

When working correctly:

1. **Type message** → Input field shows text
2. **Click Send** → Button shows loading spinner
3. **Wait 1-2 seconds** → Loading indicator in chat
4. **Response appears** → Bot message with answer
5. **Sources shown** → Policy cards below answer
6. **Confidence badge** → HIGH/MEDIUM/LOW badge

### 11. Test with Suggested Questions

Instead of typing, try clicking one of the suggested question buttons:
- "What is the password policy?"
- "Can I work remotely?"
- "What is the BYOD policy?"

This will populate the input field. Then click Send.

### 12. Check Both Terminals

**Terminal 1 (Backend):**
```
Should show:
INFO:     127.0.0.1:XXXXX - "POST /api/rag/query HTTP/1.1" 200 OK
```

**Terminal 2 (Frontend):**
```
Should show no errors
```

---

## Quick Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Documents indexed (73+ chunks)
- [ ] Browser console open
- [ ] No CORS errors
- [ ] Input field has text
- [ ] Send button is blue (not gray/disabled)
- [ ] Network tab shows request
- [ ] Backend terminal shows request

---

## Still Not Working?

### Last Resort: Complete Restart

```bash
# Terminal 1
cd backend
python init_rag.py  # Reindex
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend
rm -rf .next  # Clear Next.js cache
npm run dev

# Browser
# Hard refresh: Ctrl+Shift+R
# Open console: F12
# Try again
```

---

## Report Issue

If still not working, check console and provide:

1. Console logs (all [RAG Chat] messages)
2. Network tab screenshot
3. Backend terminal output
4. Any error messages

This will help identify the exact issue!
