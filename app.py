import os
import time
import cv2

from flask import Flask, request, jsonify, send_from_directory, Response, render_template
from werkzeug.utils import secure_filename

from src.utils import (
    setup_logger,
    validate_image,
    load_image,
    save_image,
    generate_output_filename,
    log_drowsiness_event
)

from src.landmark_detection import FaceLandmarkDetector


# Initialize App
app = Flask(__name__, static_folder="static", template_folder="templates")

# Configuration
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB
UPLOAD_FOLDER = "data/input_images"
OUTPUT_FOLDER = "outputs/images"
EVENT_FOLDER = "outputs/events"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(EVENT_FOLDER, exist_ok=True)

# Initialize Backend
setup_logger()
face_detector = FaceLandmarkDetector()

camera = None
last_log_time = 0

latest_webcam_stats = {
    "faces_detected": 0,
    "landmarks_count": 0,
    "ear": None,
    "mar": None,
    "head_pitch": None,
    "drowsy": False,
    "yawning": False,
    "head_dropped": False,
    "message": "Initializing...",
    "processing_time": 0
}


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"status": "error", "message": "Empty file"}), 400

    filename = secure_filename(file.filename)
    temp_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(temp_path)

        # Validate (file path validation)
        if not validate_image(temp_path):
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return jsonify({
                "status": "error",
                "error_type": "validation_error",
                "message": "Invalid file format. Supported formats: JPG, PNG, JPEG. Max size 10MB."
            }), 400

        start_time = time.time()

        # Load image
        image = load_image(temp_path)
        if image is None:
            return jsonify({
                "status": "error",
                "error_type": "processing_error",
                "message": "Failed to load image."
            }), 500

        # Detect landmarks + drowsiness
        detection_result = face_detector.detect_landmarks(image)

        status = detection_result.get("status", False)
        landmarks = detection_result.get("landmarks")
        annotated_image = detection_result.get("annotated_image")
        msg = detection_result.get("message", "")
        drowsiness = detection_result.get("drowsiness")

        processing_time = time.time() - start_time

        # Save output
        output_path_rel = None
        if status and annotated_image is not None:
            output_path_abs = generate_output_filename(temp_path, OUTPUT_FOLDER)

            if save_image(annotated_image, output_path_abs):
                output_path_rel = f"/outputs/{os.path.basename(output_path_abs)}"

        # For single image uploads, we evaluate drowsiness purely on thresholds since there is no framing history
        is_drowsy_image = False
        if drowsiness:
            current_ear = float(drowsiness.get("ear", 0.0))
            current_mar = float(drowsiness.get("mar", 0.0))
            current_pitch = float(drowsiness.get("head_pitch", 1.0))
            
            # Use raw thresholds to flag sleep instantly on an image
            is_drowsy_image = bool(
                (current_ear < face_detector.drowsiness_detector.ear_threshold and current_ear > 0.0) or
                # Relaxed MAR for image due to snapshot timing
                (current_mar > face_detector.drowsiness_detector.mar_threshold - 0.1) or 
                (current_pitch > face_detector.drowsiness_detector.head_pitch_threshold)
            )
            drowsiness["drowsy"] = is_drowsy_image
            drowsiness["message"] = "DROWSINESS DETECTED" if is_drowsy_image else "NORMAL"

        # Save event if drowsy
        event_data = {}
        if drowsiness and drowsiness.get("drowsy"):
            event_result = log_drowsiness_event(
                annotated_image,
                drowsiness.get("ear"),
                "image",
                EVENT_FOLDER
            )

            if event_result.get("saved"):
                event_data = {
                    "event_saved": True,
                    "event_path": event_result.get("image_path"),
                    "timestamp": event_result.get("timestamp")
                }

        # sanitize drowsiness dict to prevent numpy bool_ JSON serialization errors
        if drowsiness:
            drowsiness = {
                "ear": float(drowsiness.get("ear", 0.0)),
                "mar": float(drowsiness.get("mar", 0.0)),
                "head_pitch": float(drowsiness.get("head_pitch", 1.0)),
                "yawning": bool(drowsiness.get("yawning", False)),
                "head_dropped": bool(drowsiness.get("head_dropped", False)),
                "drowsy": bool(drowsiness.get("drowsy", False)),
                "message": str(drowsiness.get("message", ""))
            }

        response = {
            "status": "success" if status else "warning",
            "faces_detected": 1 if status else 0,
            "landmarks_count": len(landmarks) if landmarks else 0,
            "output_path": output_path_rel,
            "processing_time": round(processing_time, 2),
            "confidence": 1.0 if status else None,
            "message": msg if status else "No face detected. Please ensure face is clearly visible.",
            "drowsiness": drowsiness,
            **event_data
        }

        # shortcuts for frontend
        if drowsiness:
            response["ear"] = float(drowsiness.get("ear", 0.0))
            response["mar"] = float(drowsiness.get("mar", 0.0))
            response["head_pitch"] = float(drowsiness.get("head_pitch", 1.0))
            # For static images, if they cross threshold, they are doing the action
            response["yawning"] = bool(drowsiness.get("mar", 0) > face_detector.drowsiness_detector.mar_threshold - 0.1)
            response["head_dropped"] = bool(drowsiness.get("head_pitch", 1) > face_detector.drowsiness_detector.head_pitch_threshold)
            response["drowsy"] = bool(drowsiness.get("drowsy", False))
            response["drowsiness_message"] = str(drowsiness.get("message", ""))

        return jsonify(response)

    except Exception as e:
        return jsonify({
            "status": "error",
            "error_type": "server_error",
            "message": str(e)
        }), 500


@app.route("/outputs/<path:filename>")
def get_output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route("/webcam/start", methods=["POST"])
def start_webcam():
    global camera

    try:
        data = request.get_json() or {}
        cam_index = data.get("camera_index", 0)

        if camera is not None:
            camera.release()

        camera = cv2.VideoCapture(cam_index)

        if not camera.isOpened():
            return jsonify({"status": "error", "message": "Failed to access webcam"}), 500

        return jsonify({
            "status": "success",
            "message": "Webcam started successfully",
            "camera_index": cam_index,
            "resolution": "640x480",
            "fps_target": 30
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/webcam/stop", methods=["POST"])
def stop_webcam():
    global camera

    if camera is not None:
        camera.release()
        camera = None

    return jsonify({
        "status": "success",
        "message": "Webcam stopped successfully",
        "frames_processed": 0,
        "total_duration": "0s"
    })


@app.route("/webcam/stats", methods=["GET"])
def get_webcam_stats():
    return jsonify(latest_webcam_stats)


def generate_frames():
    global camera, latest_webcam_stats, last_log_time

    while camera is not None and camera.isOpened():
        start_t = time.time()
        success, frame = camera.read()

        if not success:
            break

        detection_result = face_detector.detect_landmarks(frame, draw_landmarks=True)

        status = detection_result.get("status", False)
        annotated_image = detection_result.get("annotated_image")
        drowsiness = detection_result.get("drowsiness")
        msg = detection_result.get("message", "")

        if not status or annotated_image is None:
            annotated_image = frame

        # If drowsy → log event snapshot (throttled)
        if drowsiness and drowsiness.get("drowsy"):
            current_t = time.time()

            if current_t - last_log_time > 2.0:
                log_drowsiness_event(
                    annotated_image,
                    drowsiness.get("ear"),
                    "webcam",
                    EVENT_FOLDER
                )
                last_log_time = current_t

            cv2.putText(
                annotated_image,
                "DROWSY!",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        # Encode JPEG for streaming
        ret, buffer = cv2.imencode(".jpg", annotated_image)
        frame_bytes = buffer.tobytes()

        # Update stats
        proc_t = time.time() - start_t

        latest_webcam_stats = {
            "faces_detected": 1 if status else 0,
            "landmarks_count": len(detection_result.get("landmarks", [])) if detection_result.get("landmarks") else 0,
            "ear": drowsiness.get("ear") if drowsiness else None,
            "mar": drowsiness.get("mar") if drowsiness else None,
            "head_pitch": drowsiness.get("head_pitch") if drowsiness else None,
            "drowsy": bool(drowsiness.get("drowsy")) if drowsiness else False,
            "yawning": bool(drowsiness.get("yawning")) if drowsiness else False,
            "head_dropped": bool(drowsiness.get("head_dropped")) if drowsiness else False,
            "message": msg if status else "No face detected",
            "processing_time": round(proc_t, 3)
        }

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.route("/webcam/frame")
def webcam_frame():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "server": "Flask",
        "version": "1.0",
        "mediapipe_loaded": True,
        "opencv_version": cv2.__version__
    })


# Error Handlers
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"status": "error", "error_type": "validation_error", "message": "Bad Request"}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "error_type": "file_not_found", "message": "Not Found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "error_type": "server_error", "message": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
