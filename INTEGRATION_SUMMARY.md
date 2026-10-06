# Frontend-to-Backend Integration Summary

## Overview
Successfully implemented the frontend-to-backend image upload flow for MCQFlash, connecting the React frontend with the FastAPI backend for MCQ answer processing.

---

## Files Changed

### Backend Files

1. **backend/main.py**
   - Added imports: `UploadFile`, `File`, `HTTPException` from FastAPI, and `CORSMiddleware`
   - Added CORS middleware configuration to allow frontend requests
   - Created new `predict_answer_from_image()` function to process uploaded images
   - Added new `POST /solve` endpoint that:
     - Accepts multipart/form-data with an image file
     - Validates file type (must be image/*)
     - Validates file size (max 10MB)
     - Saves temporary file, processes through OCR → Clef pipeline
     - Returns JSON response with message, confidence, and latency metrics
     - Cleans up temporary file after processing
   - Existing OCR → Clef-flash pipeline remains unchanged

2. **backend/pyproject.toml** (via uv)
   - Added `python-multipart` dependency for FastAPI file upload support

### Frontend Files

1. **frontend/src/App.jsx**
   - Added import for `compressImage` utility
   - Added `API_BASE_URL` from environment variable (defaults to localhost:8000)
   - Updated `handleSolve()` to:
     - Use actual image file data instead of mock data
     - Compress image before sending (1280px max, 0.80 JPEG quality)
     - Create FormData for multipart upload
     - Send POST request to `/solve` endpoint
     - Handle response and errors properly
     - Prevent duplicate submissions during loading

2. **frontend/src/components/ImageUploadCard.jsx**
   - Updated `handleFileChange()` to store both URL and file object: `{ url, file }`
   - Updated image preview to use `image.url || image` for backward compatibility

3. **frontend/src/components/AnswerCard.jsx**
   - Updated to handle backend response format:
     - Display answer message directly (backend returns full answer text)
     - Format confidence percentage properly
     - Display total latency from backend

4. **frontend/src/utils/imageCompression.js** (NEW)
   - Created utility function `compressImage()` that:
     - Takes a File object and optional max size/quality parameters
     - Uses Canvas API to resize image (max 1280px, preserves aspect ratio)
     - Converts to JPEG with 0.80 quality
     - Returns compressed image as Blob
     - Does not upscale smaller images
     - All processing done client-side with no external libraries

5. **frontend/.env** (NEW)
   - Added `VITE_API_BASE_URL=http://localhost:8000` for development

6. **frontend/.env.example** (NEW)
   - Added example environment variable file for documentation

7. **frontend/.gitignore**
   - Added `.env`, `.env.local`, `.env.*.local` to prevent committing secrets

---

## Request Flow

```
User captures image
    ↓
ImageUploadCard stores {url, file}
    ↓
User clicks "Solve MCQ"
    ↓
App.jsx handleSolve() called
    ↓
compressImage() resizes to 1280px, converts to JPEG (0.80 quality)
    ↓
FormData created with compressed image blob
    ↓
POST /solve with multipart/form-data
    ↓
FastAPI validates file type and size
    ↓
Temporary file saved to backend/temp/
    ↓
predict_answer_from_image() called
    ↓
PaddleOCR extracts text
    ↓
get_answer() sends to Cloudflare Clef-flash
    ↓
Response: {message, confidence, decision_latency, total_latency}
    ↓
Temporary file deleted
    ↓
Frontend displays answer in AnswerCard
```

---

## API Endpoint

**POST /solve**

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: `image` (file upload)

**Response:**
```json
{
  "message": "Job shop operations",
  "confidence": "78.95%",
  "decision_latency": "2194.11 ms",
  "total_latency": "4111.01 ms"
}
```

**Validation:**
- File must be image/* content type
- File size must be ≤ 10MB
- Returns 400 error for invalid files
- Returns 500 error for processing failures

---

## Image Compression

**Location:** `frontend/src/utils/imageCompression.js`

**Process:**
1. Load image into browser using FileReader
2. Calculate new dimensions (max 1280px, preserve aspect ratio)
3. Draw to Canvas with new dimensions
4. Convert to JPEG blob with 0.80 quality
5. Return compressed blob for upload

**Benefits:**
- Reduces upload size significantly (multi-MB → ~100-300KB)
- Faster upload and processing
- Still maintains OCR-quality resolution
- No external dependencies
- Client-side only (no server load)

---

## Existing Pipeline Preservation

The existing OCR → Clef-flash pipeline remains **completely unchanged**:

- `extract_text()` function unchanged
- `get_answer()` function unchanged
- PaddleOCR initialization unchanged
- Cloudflare Clef-flash API call unchanged
- Text extraction logic unchanged
- Answer extraction logic unchanged

Only added:
- New `predict_answer_from_image()` wrapper that uses existing functions
- New `/solve` endpoint that calls the wrapper
- CORS middleware for frontend access

---

## Verification

### Backend Test
```bash
curl -X POST http://localhost:8000/solve -F "image=@backend/Mcq.jpeg"
```

**Result:** ✅ Success
```json
{"message":"Job shop operations","confidence":"78.95%","decision_latency":"2194.11 ms","total_latency":"4111.01 ms"}
```

### Frontend Test
- Frontend running on http://localhost:5173
- Backend running on http://localhost:8000
- CORS configured to allow all origins (development)
- Environment variable configured

**Status:** ✅ Both servers running successfully

---

## Environment Variables

**Development (.env):**
```
VITE_API_BASE_URL=http://localhost:8000
```

**Production:**
```
VITE_API_BASE_URL=<deployed-backend-url>
```

---

## Security Considerations

1. **File Validation:**
   - Content type validation (image/* only)
   - File size limit (10MB max)
   - HTTPException for invalid files

2. **Temporary Files:**
   - Uploaded files saved to `backend/temp/`
   - Automatically deleted after processing
   - Uses unique timestamps to prevent conflicts

3. **CORS:**
   - Currently allows all origins for development
   - Should be restricted to specific frontend URL in production

4. **Environment Variables:**
   - API base URL in .env (not committed)
   - Cloudflare credentials in .env (not committed)
   - .gitignore updated to prevent committing secrets

---

## Error Handling

**Frontend:**
- Network errors caught and displayed to user
- Loading state prevents duplicate submissions
- Clear error messages for failed uploads

**Backend:**
- HTTP 400 for invalid file type or size
- HTTP 500 for processing failures
- Temporary file cleanup in finally block
- Error details returned in response

---

## Latency Optimization

The pipeline is optimized for low latency:

1. **Client-side compression** reduces upload time
2. **Direct multipart upload** (no base64 encoding)
3. **Single OCR pass** (no unnecessary re-processing)
4. **Single Clef-flash request** (no multiple LLM calls)
5. **No polling** (synchronous request/response)

No unnecessary processing steps added between camera → compression → upload → backend.

---

## Next Steps for Production

1. Update CORS configuration to specific frontend URL
2. Set production `VITE_API_BASE_URL`
3. Add authentication if required
4. Add rate limiting
5. Add request logging (without logging image contents)
6. Consider adding retry logic for failed requests
7. Add frontend error tracking/analytics
