# Face Landmark Detection - Project Specification

## 🎯 Project Overview

**Project Name:** Face Landmark Detection System  
**Project Type:** Computer Vision - Facial Analysis  
**Academic Level:** Final Year / Major Project  
**Development Status:** Active Development

---

## 📋 What This Project DOES

✅ Detects and visualizes 468 facial landmark points in real-time  
✅ Processes static images (JPG, PNG)  
✅ Processes video files (MP4, AVI)  
✅ Supports live webcam streaming with real-time detection  
✅ Displays color-coded landmark overlays on facial features  
✅ Provides processing metrics (FPS, detection confidence, processing time)  
✅ Saves processed outputs with timestamps  
✅ Runs entirely on localhost (no cloud, no external APIs)

---

## 🚫 What This Project Does NOT Do

❌ Does NOT train custom machine learning models  
❌ Does NOT require GPU or high-end hardware  
❌ Does NOT collect or store user data externally  
❌ Does NOT perform face recognition or identification  
❌ Does NOT require internet connection after setup  
❌ Does NOT use paid APIs or cloud services  
❌ Does NOT handle multiple simultaneous face tracking (limited to 1 face)

---

## 🛠️ Technology Stack (LOCKED)

### Backend
- **Language:** Python 3.8+
- **Framework:** Flask 3.0.0
- **ML Model:** MediaPipe Face Mesh (Pre-trained, 468 landmarks)
- **Computer Vision:** OpenCV 4.8.1
- **Numerical Processing:** NumPy 1.24.3

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling (Dark Modern Theme)
- **JavaScript (Vanilla)** - Interactivity
- **AJAX** - Async communication with backend

### Deployment
- **Environment:** Localhost only
- **Server:** Flask Development Server
- **Address:** http://127.0.0.1:5000
- **Port:** 5000 (default)

### Hardware Requirements
- **Minimum:** Intel i3 processor or equivalent
- **RAM:** 4GB minimum
- **Webcam:** Optional (for real-time detection)
- **GPU:** NOT required

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│              Browser (Frontend)                     │
│  - User Interface (HTML/CSS/JS)                     │
│  - File Upload / Webcam Controls                    │
│  - Result Display & Visualization                   │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP Requests/Responses
                      ↓
┌─────────────────────────────────────────────────────┐
│           Flask Server (app.py)                     │
│  - Route Handling                                   │
│  - Request Validation                               │
│  - Response Formatting                              │
└─────────────────────┬───────────────────────────────┘
                      │ Function Calls
                      ↓
┌─────────────────────────────────────────────────────┐
│         Backend Modules (src/)                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  utils.py                                    │   │
│  │  - Image I/O, Validation, Utilities          │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │  landmark_detection.py                       │   │
│  │  - MediaPipe Integration                     │   │
│  │  - Landmark Extraction                       │   │
│  │  - Visualization Logic                       │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │  face_detection.py (Optional)                │   │
│  │  - Pre-processing                            │   │
│  │  - Face Region Extraction                    │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────┘
                      │ Model Inference
                      ↓
┌─────────────────────────────────────────────────────┐
│         MediaPipe Face Mesh                         │
│  - Pre-trained Deep Learning Model                  │
│  - 468 Facial Landmarks Detection                   │
│  - CPU-optimized Inference                          │
└─────────────────────┬───────────────────────────────┘
                      │ Landmark Coordinates
                      ↓
┌─────────────────────────────────────────────────────┐
│            Processed Output                         │
│  - Annotated Images/Frames                          │
│  - Landmark Coordinate Data                         │
│  - Performance Metrics                              │
└─────────────────────────────────────────────────────┘
```

---

## 📂 Project Folder Structure

```
Face_Landmark_Detection/
│
├── data/                          # Input storage
│   ├── input_images/              # Sample/test images
│   └── sample_videos/             # Sample/test videos
│
├── src/                           # Backend logic
│   ├── face_detection.py          # Optional: Face detection preprocessing
│   ├── landmark_detection.py      # Core: MediaPipe landmark detection
│   └── utils.py                   # Utilities: I/O, validation, helpers
│
├── outputs/                       # Generated results
│   ├── images/                    # Processed images
│   └── videos/                    # Processed videos
│
├── templates/                     # Frontend HTML
│   └── index.html                 # Main dashboard page
│
├── static/                        # Frontend assets
│   ├── css/
│   │   └── style.css             # Styling (dark theme)
│   └── js/
│       └── main.js               # Interactivity & AJAX
│
├── app.py                         # Flask server (main entry point)
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

---

## 🎨 UI Design Philosophy

**Style:** Modern Technical Dashboard  
**Theme:** Dark Mode with Cyan Accents  
**Layout:** Single-page Application  
**Responsiveness:** Desktop-first, mobile-friendly

**Color Palette:**
- Primary Background: `#1a1a2e` (Dark Navy)
- Secondary Background: `#16213e` (Darker Blue)
- Accent Color: `#00d9ff` (Cyan)
- Success: `#48dbfb` (Light Blue)
- Error: `#ff6b6b` (Soft Red)
- Text: `#eaeaea` (Off-white)

---

## ⚡ Performance Targets

- **Image Processing:** < 1 second per image
- **Webcam FPS:** 25-30 FPS (target)
- **Startup Time:** < 5 seconds
- **Memory Usage:** < 500MB during operation
- **File Size Limit:** 10MB per upload

---

## 🔒 Security & Privacy

- ✅ All processing happens locally (no data leaves machine)
- ✅ No user data collection or tracking
- ✅ No external API calls or internet dependency
- ✅ Files stored only in local outputs/ directory
- ✅ User can delete outputs at any time

---

## 🎯 Primary Use Cases

1. **Academic Research** - Facial structure analysis
2. **Drowsiness Detection** - Eye aspect ratio monitoring
3. **Emotion Analysis** - Facial expression mapping
4. **AR/VR Applications** - Face mesh for overlays
5. **Medical Diagnostics** - Facial symmetry analysis
6. **Driver Monitoring** - Attention tracking systems

---

## 📊 Success Criteria

✅ **Accuracy:** Detects face in >95% of well-lit, frontal images  
✅ **Speed:** Processes images in <1 second on i3 processor  
✅ **Reliability:** Handles errors gracefully (no crashes)  
✅ **Usability:** Intuitive UI requiring no training  
✅ **Completeness:** All 3 modes (Image/Video/Webcam) functional

---

## 🚀 Future Enhancements (Out of Scope for v1.0)

- Multi-face detection support
- 3D face reconstruction
- Emotion classification model
- Mobile app version
- Cloud deployment option
- Real-time collaboration features

---

## 📝 Development Methodology

**Approach:** Specification-driven Development  
**Tools:** AI-assisted coding (iterative prompting)  
**Testing:** Manual testing + Edge case validation  
**Version Control:** Local backups (Git optional)

---

## 📅 Project Timeline

- **Week 1:** Backend development (utils, landmark detection)
- **Week 2:** Flask integration (routes, error handling)
- **Week 3:** Frontend development (HTML/CSS/JS)
- **Week 4:** Integration & testing
- **Week 5:** Polish, documentation, demo preparation

---

## ✅ Completion Checklist

### Backend
- [ ] utils.py - Image I/O and validation
- [ ] landmark_detection.py - MediaPipe integration
- [ ] app.py - Flask routes (upload, webcam)

### Frontend
- [ ] index.html - Dashboard structure
- [ ] style.css - Dark theme styling
- [ ] main.js - Upload and webcam controls

### Testing
- [ ] Image upload and processing
- [ ] Video file processing
- [ ] Webcam real-time detection
- [ ] Error handling (no face, invalid file)

### Documentation
- [ ] Code comments and docstrings
- [ ] README.md with usage instructions
- [ ] Setup guide for evaluators

---

## 📞 Project Metadata

**Developer:** [Your Name]  
**Institution:** [Your College/University]  
**Course:** [Your Course Name]  
**Submission Date:** [Target Date]  
**Contact:** [Your Email]

---

**Last Updated:** January 31, 2026  
**Version:** 1.0  
**Status:** Specification Complete - Ready for Implementation
