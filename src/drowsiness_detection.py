import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional

@dataclass
class FaceLandmarks:
    """MediaPipe Face Mesh landmark indices."""
    # Left eye indices
    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    # Right eye indices
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]
    # Inner lip indices: Left, Top, Right, Bottom
    INNER_LIP = [78, 13, 308, 14]
    # Head posture indices: Forehead, Nose tip, Chin
    HEAD_POSTURE = [10, 1, 152]

class DrowsinessDetector:
    """
    Detects drowsiness based on EAR (eyes), MAR (mouth for yawning), and Head Pitch (posture).
    """
    
    def __init__(self, ear_threshold: float = 0.22, mar_threshold: float = 0.60, head_pitch_threshold: float = 1.15, consecutive_frames: int = 15):
        """
        Initialize the drowsiness detector.
        
        Args:
            ear_threshold: Threshold below which eye is considered closed (0.22 is more robust).
            mar_threshold: Threshold above which mouth is considered open (yawning).
            head_pitch_threshold: Threshold above which head is considered dropped.
            consecutive_frames: Number of consecutive frames the condition must hold to trigger drowsiness/alarm.
        """
        self.ear_threshold = ear_threshold
        self.mar_threshold = mar_threshold
        self.head_pitch_threshold = head_pitch_threshold
        self.consecutive_frames = consecutive_frames
        
        self.closed_eyes_frames = 0
        self.yawning_frames = 0
        self.dropped_head_frames = 0
        self.drowsy_state = False
        
    def _euclidean_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points."""
        return np.linalg.norm(np.array(point1) - np.array(point2))

    def calculate_ear(self, eye_points: List[Tuple[float, float]]) -> float:
        """Calculate Eye Aspect Ratio (EAR)."""
        if len(eye_points) != 6:
            return 0.0
        A = self._euclidean_distance(eye_points[1], eye_points[5])
        B = self._euclidean_distance(eye_points[2], eye_points[4])
        C = self._euclidean_distance(eye_points[0], eye_points[3])
        if C == 0:
            return 0.0
        return (A + B) / (2.0 * C)

    def calculate_mar(self, lip_points: List[Tuple[float, float]]) -> float:
        """
        Calculate Mouth Aspect Ratio (MAR).
        Order: Left corner, Top inner, Right corner, Bottom inner
        """
        if len(lip_points) != 4:
            return 0.0
        A = self._euclidean_distance(lip_points[1], lip_points[3]) # Vertical
        C = self._euclidean_distance(lip_points[0], lip_points[2]) # Horizontal
        if C == 0:
            return 0.0
        return A / C

    def calculate_head_pitch(self, posture_points: List[Tuple[float, float]]) -> float:
        """
        Calculate Head Pitch ratio.
        Order: Forehead, Nose tip, Chin
        """
        if len(posture_points) != 3:
            return 1.0
        forehead_to_nose = self._euclidean_distance(posture_points[0], posture_points[1])
        nose_to_chin = self._euclidean_distance(posture_points[1], posture_points[2])
        if nose_to_chin == 0:
            return 1.0
        return forehead_to_nose / nose_to_chin

    def _get_coordinates(self, landmarks_dict: Dict[int, Any], indices: List[int]) -> List[Tuple[float, float]]:
        """Extract coordinates for specific indices."""
        coords = []
        for idx in indices:
            if idx in landmarks_dict:
                lm = landmarks_dict[idx]
                if hasattr(lm, 'x') and hasattr(lm, 'y'):
                    coords.append((lm.x, lm.y))
                elif isinstance(lm, (list, tuple)) and len(lm) >= 2:
                    coords.append((lm[0], lm[1]))
                elif isinstance(lm, dict) and 'x' in lm and 'y' in lm:
                    coords.append((lm['x'], lm['y']))
        return coords

    def update(self, landmarks_dict: Dict[int, Any]) -> Dict[str, Any]:
        """
        Update the detector with new frame landmarks.
        """
        if not landmarks_dict:
            return {
                "ear": 0.0, "mar": 0.0, "head_pitch": 1.0,
                "drowsy": False, "yawning": False, "head_dropped": False,
                "message": "No landmarks detected"
            }

        # Get coordinates
        left_eye_coords = self._get_coordinates(landmarks_dict, FaceLandmarks.LEFT_EYE)
        right_eye_coords = self._get_coordinates(landmarks_dict, FaceLandmarks.RIGHT_EYE)
        lip_coords = self._get_coordinates(landmarks_dict, FaceLandmarks.INNER_LIP)
        posture_coords = self._get_coordinates(landmarks_dict, FaceLandmarks.HEAD_POSTURE)

        # Calculate metrics
        avg_ear = 0.0
        if len(left_eye_coords) == 6 and len(right_eye_coords) == 6:
            avg_ear = (self.calculate_ear(left_eye_coords) + self.calculate_ear(right_eye_coords)) / 2.0
            
        mar = self.calculate_mar(lip_coords)
        head_pitch = self.calculate_head_pitch(posture_coords)

        # Check thresholds
        eyes_closed = avg_ear < self.ear_threshold
        is_yawning = mar > self.mar_threshold
        is_head_dropped = head_pitch > self.head_pitch_threshold

        # Update counters
        if eyes_closed:
            self.closed_eyes_frames += 1
        else:
            self.closed_eyes_frames = 0
            
        if is_yawning:
            self.yawning_frames += 1
        else:
            self.yawning_frames = 0
            
        if is_head_dropped:
            self.dropped_head_frames += 1
        else:
            self.dropped_head_frames = 0

        # State determination
        self.drowsy_state = False
        reasons = []

        if self.closed_eyes_frames >= self.consecutive_frames:
            self.drowsy_state = True
            reasons.append("EYES CLOSED")
        
        if self.yawning_frames >= int(self.consecutive_frames * 0.5): # Yawning triggers faster
            self.drowsy_state = True
            reasons.append("YAWNING")
            
        if self.dropped_head_frames >= self.consecutive_frames:
            self.drowsy_state = True
            reasons.append("HEAD DROPPED")

        if self.drowsy_state:
            message = "ALERT: " + " | ".join(reasons)
        else:
            message = f"EAR: {avg_ear:.2f} | MAR: {mar:.2f} | Pitch: {head_pitch:.2f}"

        return {
            "ear": float(avg_ear),
            "mar": float(mar),
            "head_pitch": float(head_pitch),
            "yawning": is_yawning,
            "head_dropped": is_head_dropped,
            "drowsy": self.drowsy_state,
            "message": message
        }
