/**
 * Face Map AI - Main Controller
 * Handles Webcam, Image Upload, and UI Updates for Driver Safety Dashboard
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration ---
    const CONFIG = {
        drowsyThreshold: 0.25, // EAR threshold for red alert
        pollInterval: 500,     // ms
        maxRiskHistory: 10     // Buffer for smoothing if needed
    };

    // --- State ---
    const state = {
        mode: 'webcam', // 'webcam' | 'image'
        isWebcamRunning: false,
        pollTimer: null,
        soundEnabled: true,
        lastEar: 0,
        isAlarmPlaying: false
    };

    // --- DOM Elements ---
    const ui = {
        // Nav
        tabs: document.querySelectorAll('.tab-btn'),

        // Panels
        panelWebcam: document.getElementById('input-panel-webcam'),
        panelImage: document.getElementById('input-panel-image'),
        visualCol: document.querySelector('.visual-col'), // Wrapper

        // Webcam Components
        webcamFeed: document.getElementById('webcam-feed'),
        webcamStatusOverlay: document.getElementById('webcam-status'),
        videoContainer: document.querySelector('.video-container'), // For red border
        btnStart: document.getElementById('start-webcam'),
        btnStop: document.getElementById('stop-webcam'),
        txtWebcamStatus: document.getElementById('webcam-status-text'),

        // Image Components
        uploadArea: document.getElementById('upload-area'),
        fileInput: document.getElementById('file-input'),
        btnProcess: document.getElementById('process-btn'),
        resultsView: document.getElementById('results-view'),
        emptyState: document.getElementById('empty-state'),
        imgOriginal: document.getElementById('original-img'),
        imgPreview: document.getElementById('preview-img'),
        imgProcessed: document.getElementById('processed-img'),

        // Insights / Stats
        cardStatus: document.getElementById('status-card'),
        txtDetectionMsg: document.getElementById('detection-message'),
        valEar: document.getElementById('stat-ear'),
        valMar: document.getElementById('stat-mar'),
        valPitch: document.getElementById('stat-pitch'),
        valFaces: document.getElementById('stat-faces'),
        valLandmarks: document.getElementById('stat-landmarks'),
        valTime: document.getElementById('stat-time'),
        riskMeter: document.getElementById('risk-meter'),
        riskText: document.getElementById('risk-text'),

        // Sound
        soundStatus: document.getElementById('sound-status'),
        indicatorSound: document.querySelector('.indicator'),
        audioAlarm: document.getElementById('alarmSound'),

        // Actions
        btnDownload: document.getElementById('download-link'),
        btnClear: document.getElementById('clear-result'),

        // Global
        toast: document.getElementById('toast'),
        loader: document.getElementById('loading-overlay')
    };

    // --- Initialization ---
    init();

    function init() {
        setupEventListeners();
        switchMode('webcam'); // Default
    }

    function setupEventListeners() {
        // Tabs
        ui.tabs.forEach(btn => {
            btn.addEventListener('click', () => switchMode(btn.dataset.mode));
        });

        // Webcam
        ui.btnStart.addEventListener('click', startWebcam);
        ui.btnStop.addEventListener('click', stopWebcam);

        // Image Upload
        ui.uploadArea.addEventListener('click', () => ui.fileInput.click());
        ui.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            ui.uploadArea.style.borderColor = 'var(--brand-primary)';
        });
        ui.uploadArea.addEventListener('dragleave', () => {
            ui.uploadArea.style.borderColor = '';
        });
        ui.uploadArea.addEventListener('drop', handleDrop);
        ui.fileInput.addEventListener('change', (e) => handleFileSelect(e.target.files[0]));
        ui.btnProcess.addEventListener('click', processImage);

        // Actions
        ui.btnClear.addEventListener('click', clearImageResults);

        // Sound Toggle (Clicking logic on the card)
        ui.soundStatus.parentElement.parentElement.addEventListener('click', toggleSound);
    }

    // --- Mode Switching ---
    function switchMode(newMode) {
        state.mode = newMode;

        // Update Tabs
        ui.tabs.forEach(t => {
            t.classList.toggle('active', t.dataset.mode === newMode);
        });

        // Update Panels
        if (newMode === 'webcam') {
            ui.panelWebcam.style.display = 'flex'; // Use flex for layout
            ui.panelWebcam.classList.add('active');
            ui.panelImage.style.display = 'none';
            ui.panelImage.classList.remove('active');

            // Reset Image View
            clearImageResults();
        } else {
            ui.panelWebcam.style.display = 'none';
            ui.panelWebcam.classList.remove('active');
            ui.panelImage.style.display = 'flex';
            ui.panelImage.classList.add('active');

            // Stop Webcam if running to save resources
            if (state.isWebcamRunning) stopWebcam();
        }
    }

    // --- Webcam Logic ---
    async function startWebcam() {
        try {
            ui.btnStart.disabled = true;
            ui.txtWebcamStatus.textContent = "Initializing Camera...";

            const response = await fetch('/webcam/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ camera_index: 0 })
            });
            const data = await response.json();

            if (data.status === 'success') {
                state.isWebcamRunning = true;

                // UI Updates
                ui.webcamStatusOverlay.style.display = 'none';
                ui.webcamFeed.style.display = 'block';
                ui.webcamFeed.src = '/webcam/frame?' + Date.now(); // Cache bust

                ui.btnStart.style.display = 'none'; // Hide start inside overlay
                ui.btnStop.disabled = false;
                ui.txtWebcamStatus.textContent = "● System Active - Monitor Running";
                ui.txtWebcamStatus.style.color = "var(--status-active)";

                showToast("Webcam Started Successfully", "success");

                // Start Stats Polling
                startPolling();
            } else {
                throw new Error(data.message);
            }
        } catch (e) {
            console.error(e);
            showToast("Failed to start webcam: " + e.message, "error");
            ui.btnStart.disabled = false;
            ui.txtWebcamStatus.textContent = "System Error";
        }
    }

    async function stopWebcam() {
        if (!state.isWebcamRunning) return;

        try {
            await fetch('/webcam/stop', { method: 'POST' });
        } catch (e) { console.warn(e); }

        state.isWebcamRunning = false;
        stopPolling();
        stopAlarm();

        // UI Reset
        ui.webcamFeed.src = "";
        ui.webcamFeed.style.display = 'none';
        ui.webcamStatusOverlay.style.display = 'flex';
        ui.videoContainer.classList.remove('drowsy-alert'); // Remove red border

        ui.btnStart.disabled = false;
        ui.btnStart.style.display = 'inline-block';
        ui.btnStop.disabled = true;

        ui.txtWebcamStatus.textContent = "System Standby";
        ui.txtWebcamStatus.style.color = "var(--text-muted)";

        resetInsights();
    }

    function startPolling() {
        if (state.pollTimer) clearInterval(state.pollTimer);
        state.pollTimer = setInterval(updateStats, CONFIG.pollInterval);
    }

    function stopPolling() {
        if (state.pollTimer) {
            clearInterval(state.pollTimer);
            state.pollTimer = null;
        }
    }

    async function updateStats() {
        try {
            const res = await fetch('/webcam/stats');
            const data = await res.json();

            renderInsights(data);

        } catch (e) {
            console.warn("Stats Poll Error", e);
        }
    }

    // --- Image Logic ---
    function handleDrop(e) {
        e.preventDefault();
        ui.uploadArea.style.borderColor = '';
        if (e.dataTransfer.files.length) handleFileSelect(e.dataTransfer.files[0]);
    }

    function handleFileSelect(file) {
        if (!file) return;
        if (!file.type.match('image.*')) {
            showToast("Please upload an image file (JPG/PNG)", "error");
            return;
        }

        // Show Preview
        const reader = new FileReader();
        reader.onload = (e) => {
            // We use original-img for preview space in this layout for now, or the preview slot
            ui.imgOriginal.src = e.target.result;
            // Also set hidden preview img if needed for consistency
            ui.imgPreview.src = e.target.result;

            // Show result view (in preview state)
            ui.uploadArea.style.display = 'none';
            ui.resultsView.style.display = 'grid';
            ui.imgProcessed.src = '/static/images/placeholder.png'; // Or keeps empty until process

            // Enable Process
            ui.btnProcess.disabled = false;
            ui.btnProcess.textContent = "🔍 Analyze Image";
        };
        reader.readAsDataURL(file);
    }

    async function processImage() {
        const file = ui.fileInput.files.length ? ui.fileInput.files[0] : null;
        if (!file) return;

        setLoading(true);

        const formData = new FormData();
        formData.append('image', file);

        try {
            const res = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.status === 'success' || data.status === 'warning') {
                // Update Processed Image
                // prevent caching
                ui.imgProcessed.src = data.output_path + "?t=" + Date.now();
                ui.btnDownload.href = data.output_path;
                ui.btnDownload.style.display = 'inline-block';

                // Show Insights
                renderInsights(data);
                showToast("Analysis Complete", "success");
            } else {
                throw new Error(data.message);
            }
        } catch (e) {
            showToast("Processing Error: " + e.message, "error");
        } finally {
            setLoading(false);
        }
    }

    function clearImageResults() {
        ui.fileInput.value = "";
        ui.uploadArea.style.display = 'flex';
        ui.resultsView.style.display = 'none';
        ui.btnProcess.disabled = true;
        ui.btnDownload.style.display = 'none';
        resetInsights();
    }

    // --- Shared Insights Logic ---
    function renderInsights(data) {
        // 1. Basic Metrics
        ui.valFaces.textContent = data.faces_detected || 0;
        ui.valLandmarks.textContent = data.landmarks_count || 0;
        ui.valTime.textContent = (data.processing_time || 0) + " s";

        // 2. EAR & Drowsiness
        let ear = 0;
        let mar = 0;
        let pitch = 1.0;
        let isDrowsy = false;
        let isYawning = false;
        let isHeadDropped = false;

        if (data.drowsiness) {
            ear = data.drowsiness.ear || 0;
            mar = data.drowsiness.mar || 0;
            pitch = data.drowsiness.head_pitch || 1.0;
            isDrowsy = data.drowsiness.drowsy;
            isYawning = data.drowsiness.yawning;
            isHeadDropped = data.drowsiness.head_dropped;
            if (data.drowsiness.message) {
                ui.txtDetectionMsg.textContent = data.drowsiness.message;
            }
        } else if (data.ear !== undefined) {
            ear = data.ear || 0;
            mar = data.mar || 0;
            pitch = data.head_pitch || 1.0;
            isDrowsy = data.drowsy;
            isYawning = data.yawning;
            isHeadDropped = data.head_dropped;
            if (data.drowsiness_message) {
                ui.txtDetectionMsg.textContent = data.drowsiness_message;
            }
        }

        ui.valEar.textContent = Number(ear).toFixed(3);
        if (ui.valMar) ui.valMar.textContent = Number(mar).toFixed(3);
        if (ui.valPitch) ui.valPitch.textContent = Number(pitch).toFixed(3);

        // 3. Status & Risk

        if (isDrowsy) {
            // TRIGGER ALARM
            ui.cardStatus.className = "insight-card main-status danger";
            ui.txtDetectionMsg.textContent = "DROWSINESS DETECTED";

            ui.riskMeter.style.width = "100%";
            ui.riskMeter.className = "risk-fill high";
            ui.riskText.textContent = "CRITICAL";

            // Visual Alarm
            if (state.mode === 'webcam') {
                ui.videoContainer.classList.add('drowsy-alert');
            }

            // Audio Alarm
            playAlarm();
        } else {
            // NORMAL
            ui.cardStatus.className = "insight-card main-status";
            ui.txtDetectionMsg.textContent = "ACTIVE / NORMAL";

            // Calc risk based on EAR (simplified visual)
            // Assuming EAR < 0.25 is drowsy. 0.25-0.3 is Warning. >0.3 is Good.
            if (ear < 0.28 && ear > 0.0) {
                ui.riskMeter.style.width = "60%";
                ui.riskMeter.className = "risk-fill medium";
                ui.riskText.textContent = "Caution";
            } else {
                ui.riskMeter.style.width = "30%";
                ui.riskMeter.className = "risk-fill low";
                ui.riskText.textContent = "Safe";
            }

            // Reset Visuals
            if (state.mode === 'webcam') {
                ui.videoContainer.classList.remove('drowsy-alert');
            }

            stopAlarm();
        }
    }

    function resetInsights() {
        ui.valFaces.textContent = "0";
        ui.valLandmarks.textContent = "0";
        ui.valTime.textContent = "--";
        ui.valEar.textContent = "--";
        if (ui.valMar) ui.valMar.textContent = "--";
        if (ui.valPitch) ui.valPitch.textContent = "--";

        ui.cardStatus.className = "insight-card main-status";
        ui.txtDetectionMsg.textContent = "WAITING...";

        ui.riskMeter.style.width = "0%";
        ui.riskText.textContent = "--";
    }

    // --- Audio Logic ---
    function toggleSound() {
        state.soundEnabled = !state.soundEnabled;
        ui.soundStatus.textContent = state.soundEnabled ? "ON" : "OFF";
        ui.indicatorSound.classList.toggle('active', state.soundEnabled);

        if (!state.soundEnabled) stopAlarm();
    }

    function playAlarm() {
        if (!state.soundEnabled) return;
        if (!state.isAlarmPlaying) {
            ui.audioAlarm.currentTime = 0; // Loop from start? Or just play
            // user interaction policy might block this if not interacted, but user clicked "Start"
            const promise = ui.audioAlarm.play();
            if (promise !== undefined) {
                promise.catch(error => {
                    console.warn("Audio play blocked", error);
                });
            }
            state.isAlarmPlaying = true;
        }
    }

    function stopAlarm() {
        if (state.isAlarmPlaying) {
            ui.audioAlarm.pause();
            ui.audioAlarm.currentTime = 0;
            state.isAlarmPlaying = false;
        }
    }

    // --- Helpers ---
    function showToast(msg, type = 'info') {
        const t = ui.toast;
        t.querySelector('.toast-message').textContent = msg;
        t.className = `toast ${type} show`;
        setTimeout(() => t.classList.remove('show'), 3000);
    }

    function setLoading(isLoading) {
        ui.loader.style.display = isLoading ? 'flex' : 'none';
    }
});
