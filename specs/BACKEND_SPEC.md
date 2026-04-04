# Backend Specification - Face Landmark Detection

## 🎯 Backend Overview

The backend is responsible for:
- Input validation and preprocessing
- Facial landmark detection using MediaPipe
- Visualization and annotation
- Output generation and storage
- Performance monitoring and error handling

**Tech Stack:** Python 3.8+ | Flask 3.0.0 | MediaPipe | OpenCV | NumPy

---

## 📦 Module Structure

```
src/
├── utils.py                # Helper functions (I/O, validation)
├── landmark_detection.py   # Core detection logic (MediaPipe)
└── face_detection.py       # Optional: Preprocessing
```

---

## 🛠️ Module 1: `utils.py`

### Purpose
Provide utility functions for file operations, validation, and common tasks.

### Functions Required

#### 1. `load_image(file_path: str) -> tuple`
```python
"""
Load image from file path using OpenCV.

Args:
    file_path (str): Absolute path to image file

Returns:
    tuple: (success: bool, image: np.ndarray or None, message: str)
    
Example:
    success, image, msg = load_image("data/input_images/test.jpg")
    if success:
        # Process image
    else:
        print(msg)  # Error message
"""
```

**Requirements:**
- Use `cv2.imread()` for loading
- Handle file not found errors
- Handle corrupted image errors
- Convert BGR to RGB if needed
- Return clear error messages

---

#### 2. `save_image(image: np.ndarray, output_path: str, filename: str = None) -> tuple`
```python
"""
Save processed image to output directory with timestamp.

Args:
    image (np.ndarray): Image to save (RGB format)
    output_path (str): Directory path (e.g., "outputs/images/")
    filename (str): Optional custom filename

Returns:
    tuple: (success: bool, saved_path: str or None, message: str)
    
Example:
    success, path, msg = save_image(processed_img, "outputs/images/", "result.jpg")
"""
```

**Requirements:**
- Auto-generate filename with timestamp if not provided
- Format: `result_YYYYMMDD_HHMMSS.jpg`
- Create output directory if doesn't exist
- Convert RGB to BGR before saving (OpenCV requirement)
- Handle write permission errors

---

#### 3. `validate_image_file(file) -> tuple`
```python
"""
Validate uploaded image file (format, size, readability).

Args:
    file: FileStorage object from Flask request

Returns:
    tuple: (valid: bool, message: str)
    
Example:
    valid, msg = validate_image_file(request.files['image'])
    if not valid:
        return jsonify({"error": msg}), 400
"""
```

**Validation Rules:**
- Allowed formats: `.jpg`, `.jpeg`, `.png`
- Max file size: 10 MB
- File must not be empty
- File must be readable

---

#### 4. `create_output_filename(original_filename: str, prefix: str = "result") -> str`
```python
"""
Generate timestamped output filename.

Args:
    original_filename (str): Original uploaded filename
    prefix (str): Prefix for output file (default: "result")

Returns:
    str: Timestamped filename
    
Example:
    filename = create_output_filename("photo.jpg", "landmarks")
    # Returns: "landmarks_20260131_143025.jpg"
"""
```

---

#### 5. `calculate_fps(start_time: float, end_time: float) -> float`
```python
"""
Calculate frames per second for performance monitoring.

Args:
    start_time (float): Processing start timestamp
    end_time (float): Processing end timestamp

Returns:
    float: FPS value (rounded to 2 decimals)
"""
```

---

#### 6. `log_error(error_message: str, error_type: str = "ERROR") -> None`
```python
"""
Log errors to console/file for debugging.

Args:
    error_message (str): Error description
    error_type (str): Type of error (ERROR, WARNING, INFO)
"""
```

**Requirements:**
- Print to console with timestamp
- Optional: Write to `logs/app.log` file
- Format: `[YYYY-MM-DD HH:MM:SS] [ERROR] Message here`

---

### Error Handling Strategy

**All functions must:**
- Return tuples with success status
- Provide clear error messages
- Never raise unhandled exceptions
- Log errors internally

---

## 🧠 Module 2: `landmark_detection.py`

### Purpose
Core facial landmark detection using MediaPipe Face Mesh.

### Global Configuration

```python
# MediaPipe Face Mesh Settings
MAX_NUM_FACES = 1
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
REFINE_LANDMARKS = False  # Set True for iris/lips refinement
STATIC_IMAGE_MODE = False  # False for video/webcam, True for images
```

---

### Functions Required

#### 1. `initialize_face_mesh() -> object`
```python
"""
Initialize MediaPipe Face Mesh model (call once at startup).

Returns:
    mp.solutions.face_mesh.FaceMesh: Initialized face mesh object

Example:
    face_mesh = initialize_face_mesh()
"""
```

**Requirements:**
- Use global configuration constants
- Initialize with `mp.solutions.face_mesh.FaceMesh()`
- Set `static_image_mode=False` for video/webcam
- Set `max_num_faces=1` (single face detection)

---

#### 2. `detect_landmarks(image: np.ndarray, face_mesh: object) -> tuple`
```python
"""
Detect 468 facial landmarks from image.

Args:
    image (np.ndarray): Input image (RGB format)
    face_mesh: Initialized MediaPipe Face Mesh object

Returns:
    tuple: (
        success: bool,
        landmarks: list of tuples [(x, y), ...] or None,
        confidence: float or None,
        message: str
    )

Example:
    success, landmarks, conf, msg = detect_landmarks(image, face_mesh)
    if success:
        print(f"Detected {len(landmarks)} landmarks with {conf}% confidence")
"""
```

**Requirements:**
- Process image with `face_mesh.process(image)`
- Extract normalized landmark coordinates
- Convert normalized (0-1) to pixel coordinates
- Handle "no face detected" gracefully
- Return landmarks as list: `[(x1, y1), (x2, y2), ..., (x468, y468)]`

---

#### 3. `draw_landmarks(image: np.ndarray, landmarks: list, color_coded: bool = True) -> np.ndarray`
```python
"""
Draw landmarks on image with optional color coding.

Args:
    image (np.ndarray): Input image (RGB)
    landmarks (list): List of (x, y) tuples
    color_coded (bool): Use different colors for face regions

Returns:
    np.ndarray: Image with landmarks drawn

Example:
    annotated_img = draw_landmarks(image, landmarks, color_coded=True)
"""
```

**Color Coding Scheme (if color_coded=True):**
- **Eyes (Left & Right):** Cyan `(0, 217, 255)`
- **Lips (Outer):** Red `(255, 107, 107)`
- **Lips (Inner):** Pink `(255, 159, 243)`
- **Nose:** Yellow `(254, 202, 87)`
- **Face Contour:** Green `(72, 219, 251)`
- **Face Oval:** White `(234, 234, 234)`

**If color_coded=False:**
- Use single color: Cyan `(0, 217, 255)`

**Drawing Specifications:**
- Point radius: 1-2 pixels
- Draw filled circles: `cv2.circle()`
- Optional: Connect landmarks with lines using MediaPipe's drawing utils

---

#### 4. `get_landmark_coordinates(landmarks: list) -> dict`
```python
"""
Extract landmark coordinates as structured data (for export).

Args:
    landmarks (list): List of (x, y) tuples

Returns:
    dict: {
        "landmark_0": {"x": 120, "y": 150},
        "landmark_1": {"x": 125, "y": 152},
        ...
    }
"""
```

**Purpose:** For saving coordinates to JSON/CSV for analysis.

---

#### 5. `process_image(image_path: str, face_mesh: object) -> dict`
```python
"""
Complete pipeline: Load → Detect → Draw → Save.

Args:
    image_path (str): Path to input image
    face_mesh: Initialized Face Mesh object

Returns:
    dict: {
        "status": "success" or "error",
        "faces_detected": int,
        "landmarks_count": int,
        "output_path": str or None,
        "processing_time": float,
        "message": str
    }
"""
```

**Pipeline Steps:**
1. Load image using `utils.load_image()`
2. Detect landmarks using `detect_landmarks()`
3. Draw landmarks using `draw_landmarks()`
4. Save result using `utils.save_image()`
5. Return comprehensive result dict

---

#### 6. `process_video_frame(frame: np.ndarray, face_mesh: object) -> tuple`
```python
"""
Process single video frame (optimized for real-time).

Args:
    frame (np.ndarray): Video frame (BGR from OpenCV)
    face_mesh: Initialized Face Mesh object

Returns:
    tuple: (annotated_frame: np.ndarray, landmarks: list or None)
"""
```

**Optimizations:**
- Skip RGB conversion if unnecessary
- Use tracking mode (static_image_mode=False)
- Minimal overhead for real-time processing

---

### Performance Constraints

**Target Metrics (i3 Processor):**
- Single image: < 1 second
- Video frame: < 40ms (25+ FPS)
- Webcam stream: 25-30 FPS

**Optimization Strategies:**
- Reuse face_mesh instance (don't reinitialize)
- Use NumPy vectorization where possible
- Avoid unnecessary image copies
- Skip frames if FPS drops (optional)

---

## 🔍 Module 3: `face_detection.py` (Optional)

### Purpose
Pre-detect face region to reduce false positives (optional enhancement).

### Functions Required

#### 1. `detect_face_region(image: np.ndarray) -> tuple`
```python
"""
Detect face bounding box using OpenCV Haar Cascades.

Args:
    image (np.ndarray): Input image

Returns:
    tuple: (face_found: bool, bbox: tuple or None)
    bbox format: (x, y, width, height)
"""
```

**Use Case:** Filter frames with no faces before landmark detection.

---

## 🔄 Data Flow Diagram

```
User Upload (Flask)
    ↓
utils.validate_image_file()
    ↓ (if valid)
utils.load_image()
    ↓
landmark_detection.detect_landmarks()
    ↓ (if face detected)
landmark_detection.draw_landmarks()
    ↓
utils.save_image()
    ↓
Return JSON response to frontend
```

---

## ⚠️ Error Handling Requirements

### Critical Error Cases

1. **File Errors**
   - File not found → Return `{"status": "error", "message": "File not found"}`
   - Unreadable file → Return `{"status": "error", "message": "Cannot read image file"}`
   - Oversized file → Return `{"status": "error", "message": "File exceeds 10MB limit"}`

2. **Detection Errors**
   - No face detected → Return `{"status": "warning", "message": "No face detected. Try better lighting or frontal view."}`
   - Low confidence → Log warning but proceed
   - Model initialization fails → Return `{"status": "error", "message": "Model initialization failed"}`

3. **Processing Errors**
   - Out of memory → Return `{"status": "error", "message": "Insufficient memory"}`
   - Unexpected exception → Log full traceback, return generic error

---

## 📊 Logging Strategy

### What to Log

**INFO Level:**
- Image processing started/completed
- Faces detected count
- Processing time

**WARNING Level:**
- No face detected
- Low detection confidence (<0.5)
- File validation issues

**ERROR Level:**
- File I/O errors
- Model errors
- Unexpected exceptions

### Log Format
```
[2026-01-31 14:30:25] [INFO] Processing image: sample.jpg
[2026-01-31 14:30:26] [INFO] Face detected | Landmarks: 468 | Time: 0.23s
[2026-01-31 14:30:30] [WARNING] No face detected in: photo2.jpg
[2026-01-31 14:30:35] [ERROR] Failed to save image: Permission denied
```

---

## 🧪 Testing Checklist

### Unit Tests Needed

- [ ] `utils.load_image()` with valid image
- [ ] `utils.load_image()` with non-existent file
- [ ] `utils.validate_image_file()` with various formats
- [ ] `landmark_detection.detect_landmarks()` with face
- [ ] `landmark_detection.detect_landmarks()` with no face
- [ ] `draw_landmarks()` output visual verification

### Edge Cases

- [ ] Grayscale images (convert to RGB)
- [ ] Very small images (<100px)
- [ ] Very large images (>4000px)
- [ ] Blurry images (low confidence)
- [ ] Side-facing profiles (may not detect)
- [ ] Multiple faces (should only detect 1)

---

## 💾 Dependencies

```python
# Core
import cv2              # OpenCV for image processing
import numpy as np      # Numerical operations
import mediapipe as mp  # Face mesh model

# Utilities
import os               # File operations
import time             # Timestamps, FPS calculation
from datetime import datetime  # Filename generation

# Flask (imported in app.py, not in src/)
from flask import Flask, request, jsonify
```

---

## ✅ Module Completion Checklist

### utils.py
- [ ] All 6 functions implemented
- [ ] Error handling in all functions
- [ ] Return tuples with status
- [ ] Timestamp generation works
- [ ] Directory creation works

### landmark_detection.py
- [ ] Face mesh initialization
- [ ] Landmark detection (468 points)
- [ ] Color-coded drawing
- [ ] Coordinate extraction
- [ ] Complete image pipeline
- [ ] Video frame processing

### face_detection.py (Optional)
- [ ] Face region detection
- [ ] Bounding box extraction

---

## 🎯 Development Priority

**Phase 1 (Essential):**
1. `utils.py` - Complete all functions
2. `landmark_detection.py` - Functions 1-3 (init, detect, draw)

**Phase 2 (Integration):**
3. `landmark_detection.process_image()` - Full pipeline
4. Test with sample images

**Phase 3 (Real-time):**
5. `landmark_detection.process_video_frame()`
6. Optimize for webcam FPS

**Phase 4 (Enhancement):**
7. `face_detection.py` - Optional preprocessing
8. Advanced error handling

---

**Last Updated:** January 31, 2026  
**Version:** 1.0  
**Status:** Ready for Implementation
