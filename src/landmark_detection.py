import cv2
import mediapipe as mp
import numpy as np
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
try:
    from src.drowsiness_detection import DrowsinessDetector
except ImportError:
    # Use relative import if running as module from parent
    from .drowsiness_detection import DrowsinessDetector

class FaceLandmarkDetector:
    """
    Detects 468 facial landmarks using MediaPipe Tasks Vision (FaceLandmarker).
    """

    def __init__(self, model_path=None):
        if model_path is None:
            # Default to data/models/face_landmarker.task relative to CWD
            model_path = os.path.join(os.getcwd(), 'data', 'models', 'face_landmarker.task')
        
        if not os.path.exists(model_path):
             raise FileNotFoundError(f"Model file not found at: {model_path}")

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1)
        self.detector = vision.FaceLandmarker.create_from_options(options)
        self.drowsiness_detector = DrowsinessDetector()

    def detect_landmarks(self, image, draw_landmarks=False):
        """
        Detects facial landmarks in the given image/frame.
        
        args:
            image (numpy.ndarray): Input image in BGR format.
            draw_landmarks (bool): Whether to draw landmarks on the annotated image.

        returns:
            dict: Structured output with keys:
                - status (bool): True if face detected, False otherwise.
                - message (str): Status message.
                - landmarks (list): List of (x, y) pixel coordinates. None if failed.
                - landmarks_count (int): Number of landmarks detected.
                - annotated_image (numpy.ndarray): Image with landmarks drawn. Original image if failed.
                - drowsiness (dict): Drowsiness detection result (ear, drowsy, message). None if no face.
        """
        status = False
        landmarks = []
        annotated_image = image.copy()
        message = "No face detected"
        drowsiness_result = None

        if image is None:
            return {
                "status": False,
                "message": "Input image is None",
                "landmarks": None,
                "landmarks_count": 0,
                "annotated_image": None,
                "drowsiness": None
            }

        try:
            # Convert BGR to RGB for MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Create MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            
            # Process
            detection_result = self.detector.detect(mp_image)

            if detection_result.face_landmarks:
                # We only want the first face (single face requirement)
                face_landmarks = detection_result.face_landmarks[0]
                
                # Convert normalized coordinates to pixel coordinates
                h, w, _ = image.shape
                landmarks_dict = {}
                for idx, lm in enumerate(face_landmarks):
                    x, y = int(lm.x * w), int(lm.y * h)
                    landmarks.append((x, y))
                    landmarks_dict[idx] = lm
                
                # Detect Drowsiness
                drowsiness_result = self.drowsiness_detector.update(landmarks_dict)

                # Draw landmarks on the annotated image manually
                if draw_landmarks:
                    self._draw_landmarks_manually(annotated_image, landmarks)
                
                status = True
                message = "Face landmarks detected successfully"
            else:
                drowsiness_result = self.drowsiness_detector.update({}) # Reset or handle no face
                message = "No face detected in the image"

        except Exception as e:
            status = False
            message = f"Error during landmark detection: {str(e)}"
            landmarks = None
            drowsiness_result = None

        return {
            "status": status,
            "message": message,
            "landmarks": landmarks,
            "landmarks_count": len(landmarks) if landmarks else 0,
            "annotated_image": annotated_image,
            "drowsiness": drowsiness_result
        }

    def _draw_landmarks_manually(self, image, landmarks):
        """
        Draws landmarks as small circles on the image.
        Uses Cyan color (255, 255, 0) in BGR.
        """
        for x, y in landmarks:
            cv2.circle(image, (x, y), 1, (255, 255, 0), -1)
