# API Specification - Face Landmark Detection

## 🌐 API Overview

**Protocol:** HTTP  
**Server:** Flask Development Server  
**Base URL:** `http://127.0.0.1:5000`  
**Content Type:** `application/json` (responses), `multipart/form-data` (file uploads)

---

## 📍 Endpoints Summary

| Endpoint | Method | Purpose | Authentication |
|----------|--------|---------|----------------|
| `/` | GET | Homepage (dashboard) | None |
| `/upload` | POST | Process uploaded image | None |
| `/webcam/start` | POST | Start webcam stream | None |
| `/webcam/stop` | POST | Stop webcam stream | None |
| `/webcam/frame` | GET | Get processed webcam frame | None |
| `/outputs/<filename>` | GET | Retrieve processed file | None |
| `/health` | GET | Server health check | None |

---

## 🔹 Endpoint Details

---

### 1. `GET /`

**Purpose:** Serve main dashboard HTML page

**Request:**
```http
GET / HTTP/1.1
Host: 127.0.0.1:5000
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: text/html

[HTML content of index.html]
```

**Flask Implementation:**
```python
@app.route('/')
def index():
    return render_template('index.html')
```

---

### 2. `POST /upload`

**Purpose:** Upload and process image file

#### Request

**Headers:**
```http
POST /upload HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary
```

**Body (Form Data):**
```
------WebKitFormBoundary
Content-Disposition: form-data; name="image"; filename="photo.jpg"
Content-Type: image/jpeg

[Binary Image Data]
------WebKitFormBoundary--
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Response (Success)

**Status Code:** `200 OK`

**JSON Body:**
```json
{
  "status": "success",
  "faces_detected": 1,
  "landmarks_count": 468,
  "output_path": "/outputs/result_20260131_143025.jpg",
  "processing_time": 0.23,
  "confidence": 0.87,
  "message": "Face detected successfully. 468 landmarks identified."
}
```

**Field Descriptions:**
- `status`: "success" or "error" or "warning"
- `faces_detected`: Number of faces found (0 or 1)
- `landmarks_count`: Total landmarks detected (468 if successful)
- `output_path`: Relative path to processed image (for download)
- `processing_time`: Time in seconds (float)
- `confidence`: Detection confidence score (0.0 to 1.0)
- `message`: Human-readable status message

#### Response (No Face Detected)

**Status Code:** `200 OK`

**JSON Body:**
```json
{
  "status": "warning",
  "faces_detected": 0,
  "landmarks_count": 0,
  "output_path": null,
  "processing_time": 0.15,
  "confidence": null,
  "message": "No face detected. Please ensure:\n- Face is clearly visible\n- Good lighting conditions\n- Frontal or near-frontal view"
}
```

#### Response (Validation Error)

**Status Code:** `400 Bad Request`

**JSON Body:**
```json
{
  "status": "error",
  "error_type": "validation_error",
  "message": "Invalid file format. Supported formats: JPG, PNG"
}
```

**Other Validation Errors:**
```json
{"status": "error", "message": "No file uploaded"}
{"status": "error", "message": "File size exceeds 10MB limit"}
{"status": "error", "message": "Empty file"}
```

#### Response (Processing Error)

**Status Code:** `500 Internal Server Error`

**JSON Body:**
```json
{
  "status": "error",
  "error_type": "processing_error",
  "message": "Failed to process image. Please try again."
}
```

---

### 3. `POST /webcam/start`

**Purpose:** Initialize webcam capture

#### Request

**Headers:**
```http
POST /webcam/start HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/json
```

**Body (Optional):**
```json
{
  "camera_index": 0
}
```
- `camera_index`: 0 for default webcam, 1+ for external cameras

#### Response (Success)

**Status Code:** `200 OK`

**JSON Body:**
```json
{
  "status": "success",
  "message": "Webcam started successfully",
  "camera_index": 0,
  "resolution": "640x480",
  "fps_target": 30
}
```

#### Response (Error)

**Status Code:** `500 Internal Server Error`

**JSON Body:**
```json
{
  "status": "error",
  "message": "Failed to access webcam. Please check camera permissions."
}
```

---

### 4. `POST /webcam/stop`

**Purpose:** Stop webcam capture and release resources

#### Request

```http
POST /webcam/stop HTTP/1.1
Host: 127.0.0.1:5000
```

#### Response (Success)

**Status Code:** `200 OK`

**JSON Body:**
```json
{
  "status": "success",
  "message": "Webcam stopped successfully",
  "frames_processed": 1250,
  "total_duration": "42.5s"
}
```

---

### 5. `GET /webcam/frame`

**Purpose:** Get current processed webcam frame (for live streaming)

#### Request

```http
GET /webcam/frame HTTP/1.1
Host: 127.0.0.1:5000
```

#### Response (MJPEG Stream)

**Status Code:** `200 OK`

**Headers:**
```http
Content-Type: multipart/x-mixed-replace; boundary=frame
```

**Body (Continuous Stream):**
```
--frame
Content-Type: image/jpeg

[JPEG Image Data]
--frame
Content-Type: image/jpeg

[JPEG Image Data]
--frame
...
```

**Flask Implementation Pattern:**
```python
def generate_frames():
    while webcam_active:
        success, frame = camera.read()
        if success:
            # Process frame with landmarks
            processed_frame = process_video_frame(frame, face_mesh)
            
            # Encode to JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/webcam/frame')
def webcam_frame():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')
```

**Frontend HTML:**
```html
<img id="webcam-feed" src="/webcam/frame" alt="Webcam Feed">
```

---

### 6. `GET /outputs/<filename>`

**Purpose:** Retrieve processed image file

#### Request

```http
GET /outputs/result_20260131_143025.jpg HTTP/1.1
Host: 127.0.0.1:5000
```

#### Response (Success)

**Status Code:** `200 OK`

**Headers:**
```http
Content-Type: image/jpeg
Content-Disposition: inline; filename="result_20260131_143025.jpg"
```

**Body:** [Binary Image Data]

#### Response (Not Found)

**Status Code:** `404 Not Found`

**JSON Body:**
```json
{
  "status": "error",
  "message": "File not found"
}
```

**Flask Implementation:**
```python
from flask import send_from_directory

@app.route('/outputs/<path:filename>')
def get_output_file(filename):
    return send_from_directory('outputs/images', filename)
```

---

### 7. `GET /health`

**Purpose:** Check server status (for monitoring/debugging)

#### Request

```http
GET /health HTTP/1.1
Host: 127.0.0.1:5000
```

#### Response

**Status Code:** `200 OK`

**JSON Body:**
```json
{
  "status": "healthy",
  "server": "Flask",
  "version": "1.0",
  "uptime": "01:23:45",
  "mediapipe_loaded": true,
  "opencv_version": "4.8.1"
}
```

---

## 🔄 Request/Response Workflows

### Workflow 1: Image Upload

```
Frontend                          Backend
   |                                 |
   |---(1) POST /upload (image)---->|
   |                                 |--- Load & Validate
   |                                 |--- Detect Landmarks
   |                                 |--- Draw & Save
   |                                 |
   |<--(2) JSON Response------------|
   |     {status, output_path, ...} |
   |                                 |
   |---(3) Display Result---------->|
   |     <img src="/outputs/...">   |
```

### Workflow 2: Webcam Stream

```
Frontend                          Backend
   |                                 |
   |---(1) POST /webcam/start------>|
   |                                 |--- Initialize Camera
   |<--(2) {status: "success"}------|
   |                                 |
   |---(3) Request Frame----------->|
   |     GET /webcam/frame          |
   |                                 |--- Capture Frame
   |                                 |--- Detect & Draw
   |<--(4) MJPEG Stream-------------|
   |     (continuous frames)         |
   |                                 |
   |---(5) POST /webcam/stop------->|
   |                                 |--- Release Camera
   |<--(6) {status: "success"}------|
```

---

## ⚠️ Error Response Standards

### Error Response Format

All errors follow this JSON structure:

```json
{
  "status": "error",
  "error_type": "category_of_error",
  "message": "Human-readable description",
  "details": "Optional technical details"
}
```

### Error Categories

| Error Type | HTTP Status | Example Message |
|------------|-------------|-----------------|
| `validation_error` | 400 | "Invalid file format" |
| `file_not_found` | 404 | "Requested file does not exist" |
| `processing_error` | 500 | "Landmark detection failed" |
| `camera_error` | 500 | "Cannot access webcam" |
| `server_error` | 500 | "Unexpected server error" |

---

## 🔒 CORS Configuration

**Not Required** - Frontend and backend on same origin (localhost:5000)

If needed in future:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

---

## 📊 Response Time Targets

| Endpoint | Target | Maximum Acceptable |
|----------|--------|-------------------|
| `GET /` | < 50ms | 200ms |
| `POST /upload` | < 1s | 3s |
| `GET /webcam/frame` | < 40ms | 100ms |
| `POST /webcam/start` | < 500ms | 2s |

---

## 🧪 Testing Examples

### Test 1: Upload Valid Image

**cURL Command:**
```bash
curl -X POST http://127.0.0.1:5000/upload \
  -F "image=@test_image.jpg"
```

**Expected Response:**
```json
{
  "status": "success",
  "faces_detected": 1,
  "landmarks_count": 468,
  "output_path": "/outputs/result_20260131_143025.jpg"
}
```

### Test 2: Upload Invalid File

**cURL Command:**
```bash
curl -X POST http://127.0.0.1:5000/upload \
  -F "image=@document.pdf"
```

**Expected Response:**
```json
{
  "status": "error",
  "message": "Invalid file format. Supported formats: JPG, PNG"
}
```

### Test 3: Health Check

**cURL Command:**
```bash
curl http://127.0.0.1:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "mediapipe_loaded": true
}
```

---

## 📝 Frontend Integration Examples

### JavaScript: Upload Image

```javascript
async function uploadImage(file) {
    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Display result
            document.getElementById('result-img').src = data.output_path;
            document.getElementById('stats').innerHTML = 
                `Faces: ${data.faces_detected} | Landmarks: ${data.landmarks_count}`;
        } else {
            // Show error
            alert(data.message);
        }
    } catch (error) {
        console.error('Upload failed:', error);
        alert('Upload failed. Please try again.');
    }
}
```

### JavaScript: Webcam Control

```javascript
async function startWebcam() {
    const response = await fetch('/webcam/start', { method: 'POST' });
    const data = await response.json();
    
    if (data.status === 'success') {
        document.getElementById('webcam-feed').src = '/webcam/frame';
        document.getElementById('status').textContent = 'Webcam Active';
    }
}

async function stopWebcam() {
    const response = await fetch('/webcam/stop', { method: 'POST' });
    const data = await response.json();
    
    if (data.status === 'success') {
        document.getElementById('webcam-feed').src = '';
        document.getElementById('status').textContent = 'Webcam Stopped';
    }
}
```

---

## 🎯 API Development Checklist

### Phase 1: Basic Routes
- [ ] `GET /` - Homepage rendering
- [ ] `POST /upload` - Image processing
- [ ] `GET /outputs/<filename>` - File serving

### Phase 2: Webcam Integration
- [ ] `POST /webcam/start` - Camera initialization
- [ ] `GET /webcam/frame` - Frame streaming
- [ ] `POST /webcam/stop` - Camera release

### Phase 3: Error Handling
- [ ] Validation errors (400)
- [ ] Not found errors (404)
- [ ] Server errors (500)
- [ ] Graceful degradation

### Phase 4: Monitoring
- [ ] `GET /health` - Health check
- [ ] Request logging
- [ ] Performance metrics

---

## 📌 Important Notes

### File Upload Limits
```python
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
```

### Static File Serving
```python
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
```

### Debug Mode (Development Only)
```python
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
```

**⚠️ Never use debug=True in production!**

---

**Last Updated:** January 31, 2026  
**Version:** 1.0  
**Status:** Ready for Implementation
