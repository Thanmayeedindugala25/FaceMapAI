# Frontend Specification - Face Landmark Detection

## 🎨 Frontend Overview

**UI Style:** Modern Technical Dashboard  
**Layout Type:** Single-page Application (SPA)  
**Theme:** Dark Mode with Cyan Accents  
**Responsiveness:** Desktop-first, mobile-friendly  
**Tech Stack:** HTML5 + CSS3 + Vanilla JavaScript

---

## 🎯 Design Principles

1. **Clarity** - Every element has clear purpose
2. **Feedback** - Immediate visual response to user actions
3. **Consistency** - Uniform styling and behavior
4. **Accessibility** - Readable text, clear contrast
5. **Performance** - Fast loading, smooth animations

---

## 🎨 Color Palette

### Primary Colors
```css
--bg-primary: #1a1a2e;       /* Dark Navy Background */
--bg-secondary: #16213e;     /* Darker Blue Cards */
--bg-tertiary: #0f3460;      /* Accent Backgrounds */
```

### Accent Colors
```css
--accent-primary: #00d9ff;   /* Cyan - Primary Actions */
--accent-secondary: #3282b8; /* Blue - Secondary Elements */
--accent-tertiary: #0f4c75;  /* Dark Blue - Borders */
```

### Status Colors
```css
--success: #48dbfb;          /* Light Blue - Success */
--warning: #feca57;          /* Yellow - Warnings */
--error: #ff6b6b;            /* Soft Red - Errors */
--info: #54a0ff;             /* Blue - Information */
```

### Text Colors
```css
--text-primary: #eaeaea;     /* Off-white - Main Text */
--text-secondary: #a4b0be;   /* Gray - Secondary Text */
--text-muted: #747d8c;       /* Dark Gray - Muted Text */
```

### Landmark Colors (for visualization)
```css
--landmark-eyes: #00d9ff;    /* Cyan */
--landmark-lips-outer: #ff6b6b;  /* Red */
--landmark-lips-inner: #ff9ff3;  /* Pink */
--landmark-nose: #feca57;    /* Yellow */
--landmark-contour: #48dbfb; /* Green-blue */
--landmark-oval: #eaeaea;    /* White */
```

---

## 📐 Layout Structure

### Overall Layout (1920x1080 Desktop)

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER (80px height)                                       │
│  - Logo/Title (left)                                        │
│  - Mode Tabs (center)                                       │
│  - Info Badge (right)                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────┐  ┌──────────────────────────┐    │
│  │                      │  │                          │    │
│  │   INPUT PANEL        │  │    OUTPUT PANEL          │    │
│  │   (40% width)        │  │    (60% width)           │    │
│  │                      │  │                          │    │
│  │   - Upload Area      │  │   - Result Display       │    │
│  │   - Webcam Preview   │  │   - Landmark Overlay     │    │
│  │   - Controls         │  │   - Comparison View      │    │
│  │                      │  │                          │    │
│  │   (min-height:600px) │  │   (min-height:600px)     │    │
│  │                      │  │                          │    │
│  └──────────────────────┘  └──────────────────────────┘    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  STATS BAR (60px height)                                    │
│  - Metrics: Faces | Landmarks | FPS | Time                  │
└─────────────────────────────────────────────────────────────┘
```

**Spacing:**
- Page margin: 20px
- Panel gap: 20px
- Internal padding: 30px
- Element spacing: 15px

---

## 🧩 Component Specifications

---

### 1. Header Component

**HTML Structure:**
```html
<header class="app-header">
    <div class="header-left">
        <div class="logo">🎯</div>
        <h1 class="title">Face Landmark Detection</h1>
    </div>
    
    <div class="header-center">
        <div class="mode-tabs">
            <button class="tab-btn active" data-mode="image">📷 Image</button>
            <button class="tab-btn" data-mode="video">🎬 Video</button>
            <button class="tab-btn" data-mode="webcam">📹 Webcam</button>
        </div>
    </div>
    
    <div class="header-right">
        <div class="tech-badge">
            <span>Powered by</span>
            <strong>MediaPipe</strong>
        </div>
    </div>
</header>
```

**Styling Requirements:**
- Background: `var(--bg-secondary)`
- Height: 80px
- Flex layout with space-between
- Sticky position (stays on top when scrolling)
- Box shadow: `0 2px 10px rgba(0, 0, 0, 0.3)`

**Tab Button States:**
- Default: `background: transparent`, `color: var(--text-secondary)`
- Hover: `background: var(--bg-tertiary)`, `transform: translateY(-2px)`
- Active: `background: var(--accent-primary)`, `color: var(--bg-primary)`, `font-weight: bold`

---

### 2. Input Panel Component

**Layout Variants (based on mode):**

#### Mode: Image Upload

```html
<div class="input-panel">
    <h2 class="panel-title">📤 Upload Image</h2>
    
    <div class="upload-area" id="upload-area">
        <div class="upload-icon">📁</div>
        <p class="upload-text">Drag & Drop Image Here</p>
        <p class="upload-subtext">or</p>
        <button class="btn btn-secondary">Browse Files</button>
        <input type="file" id="file-input" accept="image/*" hidden>
    </div>
    
    <div class="file-info">
        <p class="info-text">Supported: JPG, PNG</p>
        <p class="info-text">Max Size: 10MB</p>
    </div>
    
    <button class="btn btn-primary" id="process-btn" disabled>
        🔍 Detect Landmarks
    </button>
    
    <div class="preview-container" id="preview" style="display:none;">
        <img id="preview-img" alt="Preview">
    </div>
</div>
```

**Upload Area States:**

1. **Default State:**
   - Border: `2px dashed var(--accent-tertiary)`
   - Background: `transparent`
   - Padding: 40px
   - Border-radius: 12px

2. **Hover State:**
   - Border: `2px solid var(--accent-primary)`
   - Background: `rgba(0, 217, 255, 0.05)`
   - Cursor: pointer

3. **Drag Over State:**
   - Border: `3px solid var(--accent-primary)`
   - Background: `rgba(0, 217, 255, 0.15)`
   - Scale: 1.02

4. **File Selected State:**
   - Border: `2px solid var(--success)`
   - Background: `rgba(72, 219, 251, 0.1)`
   - Show preview image

#### Mode: Webcam

```html
<div class="input-panel">
    <h2 class="panel-title">📹 Webcam Feed</h2>
    
    <div class="webcam-container">
        <video id="webcam-preview" autoplay playsinline></video>
        <div class="webcam-overlay" id="webcam-status">
            <div class="status-icon">📷</div>
            <p>Click Start to begin</p>
        </div>
    </div>
    
    <div class="webcam-controls">
        <button class="btn btn-primary" id="start-webcam">
            ▶️ Start Webcam
        </button>
        <button class="btn btn-secondary" id="stop-webcam" disabled>
            ⏹️ Stop
        </button>
        <button class="btn btn-secondary" id="capture-frame" disabled>
            📸 Capture
        </button>
    </div>
    
    <div class="webcam-info">
        <div class="info-item">
            <span class="label">Status:</span>
            <span class="value" id="webcam-status-text">Inactive</span>
        </div>
        <div class="info-item">
            <span class="label">Recording:</span>
            <span class="value" id="recording-time">00:00</span>
        </div>
    </div>
</div>
```

**Webcam Container:**
- Aspect ratio: 4:3 or 16:9
- Background: `var(--bg-tertiary)`
- Border-radius: 8px
- Overflow: hidden

**Recording Indicator:**
- Red pulsing dot when active
- Animation: `pulse 2s ease-in-out infinite`

---

### 3. Output Panel Component

```html
<div class="output-panel">
    <h2 class="panel-title">📊 Detection Results</h2>
    
    <div class="results-container" id="results">
        <!-- Empty State -->
        <div class="empty-state" id="empty-state">
            <div class="empty-icon">🎯</div>
            <p class="empty-text">No results yet</p>
            <p class="empty-subtext">Upload an image or start webcam to begin</p>
        </div>
        
        <!-- Results View (hidden by default) -->
        <div class="results-view" id="results-view" style="display:none;">
            <div class="image-comparison">
                <div class="comparison-item">
                    <p class="comparison-label">Original</p>
                    <img id="original-img" alt="Original">
                </div>
                <div class="comparison-item">
                    <p class="comparison-label">Processed</p>
                    <img id="processed-img" alt="Processed">
                </div>
            </div>
            
            <div class="result-actions">
                <button class="btn btn-secondary" id="toggle-overlay">
                    👁️ Toggle Overlay
                </button>
                <button class="btn btn-primary" id="download-result">
                    💾 Download
                </button>
                <button class="btn btn-secondary" id="clear-result">
                    🗑️ Clear
                </button>
            </div>
            
            <div class="detection-info">
                <div class="info-card success">
                    <div class="info-icon">✅</div>
                    <div class="info-content">
                        <p class="info-title">Face Detected</p>
                        <p class="info-value" id="detection-message">
                            468 landmarks identified
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

**Image Comparison:**
- Display: Grid (2 columns)
- Gap: 20px
- Each image max-width: 100%
- Border: 1px solid `var(--accent-tertiary)`
- Border-radius: 8px

---

### 4. Stats Bar Component

```html
<div class="stats-bar">
    <div class="stat-item">
        <span class="stat-icon">👤</span>
        <span class="stat-label">Faces:</span>
        <span class="stat-value" id="stat-faces">0</span>
    </div>
    
    <div class="stat-separator">|</div>
    
    <div class="stat-item">
        <span class="stat-icon">📍</span>
        <span class="stat-label">Landmarks:</span>
        <span class="stat-value" id="stat-landmarks">0</span>
    </div>
    
    <div class="stat-separator">|</div>
    
    <div class="stat-item">
        <span class="stat-icon">⚡</span>
        <span class="stat-label">FPS:</span>
        <span class="stat-value" id="stat-fps">--</span>
    </div>
    
    <div class="stat-separator">|</div>
    
    <div class="stat-item">
        <span class="stat-icon">⏱️</span>
        <span class="stat-label">Time:</span>
        <span class="stat-value" id="stat-time">--</span>
    </div>
</div>
```

**Styling:**
- Background: `var(--bg-secondary)`
- Position: Fixed bottom
- Width: 100%
- Display: Flex with space-around
- Box shadow: `0 -2px 10px rgba(0, 0, 0, 0.3)`

---

## 🎭 Interactive Elements

### Button Styles

**Primary Button:**
```css
.btn-primary {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    color: var(--bg-primary);
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 217, 255, 0.4);
}

.btn-primary:active {
    transform: translateY(0);
}

.btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}
```

**Secondary Button:**
```css
.btn-secondary {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border: 1px solid var(--accent-tertiary);
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-secondary:hover {
    background: var(--accent-tertiary);
    border-color: var(--accent-primary);
}
```

---

### Loading States

**Spinner Animation:**
```html
<div class="loading-spinner">
    <div class="spinner"></div>
    <p>Processing...</p>
</div>
```

```css
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.spinner {
    border: 4px solid var(--bg-tertiary);
    border-top: 4px solid var(--accent-primary);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}
```

**Progress Bar:**
```html
<div class="progress-bar">
    <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
</div>
```

```css
.progress-bar {
    width: 100%;
    height: 4px;
    background: var(--bg-tertiary);
    border-radius: 2px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
    transition: width 0.3s ease;
}
```

---

### Notification Toast

```html
<div class="toast" id="toast">
    <div class="toast-icon">ℹ️</div>
    <p class="toast-message">Message here</p>
</div>
```

```css
.toast {
    position: fixed;
    top: 100px;
    right: 20px;
    background: var(--bg-secondary);
    border-left: 4px solid var(--accent-primary);
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    opacity: 0;
    transform: translateX(400px);
    transition: all 0.3s ease;
}

.toast.show {
    opacity: 1;
    transform: translateX(0);
}

.toast.success { border-left-color: var(--success); }
.toast.error { border-left-color: var(--error); }
.toast.warning { border-left-color: var(--warning); }
```

---

## 🎬 Animations & Transitions

### Fade In
```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fadeIn 0.5s ease-out;
}
```

### Pulse (for recording indicator)
```css
@keyframes pulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.7;
        transform: scale(1.1);
    }
}

.recording-indicator {
    width: 12px;
    height: 12px;
    background: var(--error);
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}
```

### Skeleton Loading
```css
@keyframes shimmer {
    0% {
        background-position: -1000px 0;
    }
    100% {
        background-position: 1000px 0;
    }
}

.skeleton {
    background: linear-gradient(
        90deg,
        var(--bg-tertiary) 0%,
        var(--bg-secondary) 50%,
        var(--bg-tertiary) 100%
    );
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}
```

---

## 📱 Responsive Design

### Breakpoints

```css
/* Desktop (default) */
@media (min-width: 1200px) { /* Current styles */ }

/* Tablet */
@media (max-width: 1199px) and (min-width: 768px) {
    .main-content {
        flex-direction: column;
    }
    
    .input-panel,
    .output-panel {
        width: 100%;
    }
}

/* Mobile */
@media (max-width: 767px) {
    .header-center {
        display: none; /* Hide tabs, use dropdown */
    }
    
    .stats-bar {
        flex-wrap: wrap;
        height: auto;
    }
    
    .image-comparison {
        grid-template-columns: 1fr;
    }
}
```

---

## ⚙️ JavaScript Functionality

### Required Functions

#### 1. File Upload Handler
```javascript
function handleFileUpload(file) {
    // Validate file
    // Show preview
    // Enable process button
}
```

#### 2. Image Processing
```javascript
async function processImage() {
    // Show loading state
    // Send to backend
    // Handle response
    // Display results
    // Update stats
}
```

#### 3. Webcam Control
```javascript
async function startWebcam() {
    // Request camera access
    // Initialize video stream
    // Start processing loop
}

async function stopWebcam() {
    // Stop stream
    // Release camera
    // Clean up
}
```

#### 4. Result Display
```javascript
function displayResults(data) {
    // Show original vs processed
    // Update stats bar
    // Enable download button
}
```

#### 5. Notification System
```javascript
function showToast(message, type = 'info') {
    // Create toast element
    // Show with animation
    // Auto-hide after 3s
}
```

---

## ✅ Frontend Development Checklist

### Phase 1: Structure
- [ ] Create `index.html` with all components
- [ ] Define semantic HTML structure
- [ ] Add proper accessibility attributes

### Phase 2: Styling
- [ ] Create `style.css` with color variables
- [ ] Style all components
- [ ] Add hover/active states
- [ ] Implement responsive design

### Phase 3: Interactivity
- [ ] File upload (drag & drop + browse)
- [ ] Image preview
- [ ] Process button click handler
- [ ] Webcam start/stop
- [ ] Result display toggling

### Phase 4: Backend Integration
- [ ] AJAX upload function
- [ ] Response parsing
- [ ] Error handling
- [ ] Loading states

### Phase 5: Polish
- [ ] Animations and transitions
- [ ] Toast notifications
- [ ] Empty states
- [ ] Cross-browser testing

---

## 🎯 User Experience Goals

1. **First Impression:** Modern, professional, trustworthy
2. **Ease of Use:** Intuitive, no learning curve needed
3. **Feedback:** Every action has visible response
4. **Performance:** Fast loading, smooth interactions
5. **Reliability:** Graceful error handling, no crashes

---

**Last Updated:** January 31, 2026  
**Version:** 1.0  
**Status:** Ready for Implementation
