# 🧠 FaceMapAI — Real-Time Driver Drowsiness Detection System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
<div align="center">

[![IRJET Published](https://img.shields.io/badge/IRJET-Vol.13%20|%20Issue%2003%20|%20IF%3A8.315-red?style=for-the-badge)](https://www.irjet.net/volume13-issue03)
**📄 Published:** "Face Map AI – A Deep Convolutional Neural Network with Adaptive Attention for Robust Real-Time Face Landmark Detection"  
**Journal:** IRJET | **Volume:** 13 | **Issue:** 03 | **Month:** March 2026 | **Impact Factor:** 8.315

</div>
**A deep learning-powered computer vision system that detects driver drowsiness in real time using facial landmark analysis — no specialized hardware required.**

[🚀 Features](#-features) • [⚙️ How It Works](#️-how-it-works) • [📊 Results](#-results) • [🛠️ Setup](#️-setup--installation) • [👥 Team](#-team)

</div>

---

## 🚨 The Problem

> Driver fatigue is responsible for approximately **20% of all serious road accidents** worldwide.

Traditional monitoring systems rely on:
- ❌ Driver self-awareness (unreliable when fatigued)
- ❌ Vehicle behavior sensors (reactive, not proactive)
- ❌ Expensive specialized hardware

---

## ✅ Our Solution

FaceMapAI continuously monitors a driver's face via a standard webcam and detects drowsiness using **3 independent physiological signals** — before it becomes dangerous.

<div align="center">

![System Architecture](screenshots/architecture.png)
*Fig: End-to-end system architecture of FaceMapAI*

</div>

---

## 🚀 Features

- 👁️ **Real-time facial landmark detection** — 468 3D points tracked per frame
- 📊 **Multi-signal drowsiness detection** — EAR + MAR + Head Pose
- 🔔 **Multi-modal alerts** — Audio + Visual warnings
- 🖼️ **Dual input modes** — Live webcam & static image upload
- 📁 **Event logging** — Snapshots + timestamps saved automatically
- 💻 **No GPU required** — Runs on standard laptops

---

## ⚙️ How It Works

### Three Detection Signals

| Signal | What It Measures | Drowsy Threshold |
|--------|-----------------|-----------------|
| 👁️ **Eye Aspect Ratio (EAR)** | Eyelid closure degree | EAR < 0.22 for 20+ frames |
| 👄 **Mouth Aspect Ratio (MAR)** | Yawning detection | MAR > 0.60 |
| 🗣️ **Head Pitch Ratio** | Forward head drooping | Ratio > 1.15 |

### Processing Pipeline
```
Webcam Input → Frame Capture → MediaPipe Face Mesh (468 landmarks)
→ EAR + MAR + Head Pose Calculation → Drowsiness Classification
→ Audio + Visual Alert → Event Log
```

---

## 📊 Results

### 🟢 Active / Normal State
<div align="center">

![Normal State](screenshots/normal.png)
*Driver alert — EAR: 0.323 | MAR: 0.004 | Risk: Safe*

</div>

### 🔴 Drowsiness Detected
<div align="center">

![Drowsy State](screenshots/drowsy.png)
*Drowsiness detected — EAR: 0.156 | Risk: CRITICAL | Alert triggered*

</div>

### 🖼️ Image-Based Analysis
<div align="center">

![Image Analysis](screenshots/image_analysis.png)
*Static image analysis mode with side-by-side comparison*

</div>

### Performance Metrics

| Metric | Value |
|--------|-------|
| Alert Response Time | ~1–2 seconds |
| Landmarks Tracked | 468 (3D) |
| Input Modes | Webcam + Image Upload |
| Hardware Required | Standard webcam only |
| GPU Required | ❌ No |

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.9+
- Webcam

### Steps
```bash
# 1. Clone the repository
git clone https://github.com/Thanmayeedindugala25/FaceMapAI.git
cd FaceMapAI

# 2. Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Then open your browser and go to:
```
http://127.0.0.1:5000
```

---

## 📁 Project Structure
```
FaceMapAI/
├── app.py                  # Flask backend + API routes
├── requirements.txt        # Python dependencies
├── src/
│   ├── face_detection.py   # Face detection module
│   ├── landmark_detection.py # 468-point landmark engine
│   └── utils.py            # EAR, MAR, Head Pose calculations
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── sounds/alarm.mp3    # Drowsiness alert sound
├── templates/
│   └── index.html          # Frontend UI
└── screenshots/            # Demo images
```

---

## 🔮 Future Scope

- 📱 Mobile app + cloud dashboard for fleet monitoring
- 🚗 IoT integration with vehicle safety systems
- 👥 Multi-face monitoring for buses/trucks
- 🌙 Low-light & night driving enhancement
- 🧠 Deep learning classifier on top of geometric metrics

---

## 👥 Team
**D. Thanmayee · C. Jayasimha · D. Ramya Sri · G.K. Vamsi Reddy**  
B.Tech CSE (AIML) — Malla Reddy University, 2026  
Guide: Prof. T. Vinay Simha Reddy

---
<div align="center">
Made with ❤️ for safer roads
</div>
## 📚 References

Built on top of research by Google MediaPipe team, and validated by published work on EAR-based drowsiness detection (Soukupová & Čech, 2016) and MediaPipe-based driver monitoring systems.

---

<div align="center">
Made with ❤️ for safer roads | Malla Reddy University, 2026
</div>
