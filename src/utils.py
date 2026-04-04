import os
import cv2
import logging
from datetime import datetime
from pathlib import Path
import sys

def setup_logger(log_dir="logs", log_file="app.log"):
    """
    Configures the logger to write to a file and stdout.
    Creates the log directory if it does not exist.
    """
    try:
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_path = os.path.join(log_dir, log_file)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.info("Logger initialized.")
    except Exception as e:
        print(f"Error setting up logger: {e}")

def validate_image(file_path):
    """
    Validates the image file based on extension and size.
    Allowed extensions: .jpg, .jpeg, .png
    Max size: 10MB

    Args:
        file_path (str): Path to the image file.

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logging.error(f"File not found: {file_path}")
            return False

        # Check extension
        allowed_extensions = {'.jpg', '.jpeg', '.png'}
        if path.suffix.lower() not in allowed_extensions:
            logging.error(f"Invalid file extension: {path.suffix}. Allowed: {allowed_extensions}")
            return False

        # Check size (10MB = 10 * 1024 * 1024 bytes)
        max_size = 10 * 1024 * 1024
        if path.stat().st_size > max_size:
            logging.error(f"File too large: {path.stat().st_size / (1024*1024):.2f}MB. Max: 10MB")
            return False

        return True
    except Exception as e:
        logging.error(f"Error validating image: {e}")
        return False

def load_image(file_path):
    """
    Loads an image from disk using OpenCV.

    Args:
        file_path (str): Path to the image file.

    Returns:
        numpy.ndarray: The loaded image, or None if failed.
    """
    try:
        image = cv2.imread(str(file_path))
        if image is None:
            logging.error(f"Failed to load image: {file_path}")
            return None
        return image
    except Exception as e:
        logging.error(f"Error loading image: {e}")
        return None

def generate_output_filename(original_path, output_dir="output"):
    """
    Generates a timestamped output filename.

    Args:
        original_path (str): Path to the original input file.
        output_dir (str): Directory where the output will be saved.

    Returns:
        str: Full path for the output file.
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        path = Path(original_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{path.stem}_processed_{timestamp}{path.suffix}"
        return os.path.join(output_dir, filename)
    except Exception as e:
        logging.error(f"Error generating output filename: {e}")
        return None

def save_image(image, output_path):
    """
    Saves an image to disk using OpenCV.

    Args:
        image (numpy.ndarray): The image data.
        output_path (str): Path to save the image.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        if image is None:
            logging.error("No image data to save.")
            return False

        success = cv2.imwrite(output_path, image)
        if success:
            logging.info(f"Image saved to: {output_path}")
        else:
            logging.error(f"Failed to save image to: {output_path}")
        return success
    except Exception as e:
        logging.error(f"Error saving image: {e}")
        return False

def log_drowsiness_event(image, ear, mode="webcam", output_dir="outputs/events"):
    """
    Logs a drowsiness event: saves the snapshot and updates the JSON log.
    
    Args:
        image (numpy.ndarray): The image frame to save.
        ear (float): The EAR value detected.
        mode (str): 'webcam' or 'image'.
        output_dir (str): Base directory for events.
        
    Returns:
        dict: {
            "saved": bool,
            "image_path": str (relative path for frontend),
            "timestamp": str
        }
    """
    import json
    
    try:
        # 1. Setup paths
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp_iso = datetime.now().isoformat()
        timestamp_safe = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # 2. Save Snapshot
        filename = f"drowsy_{mode}_{timestamp_safe}.jpg"
        abs_image_path = os.path.join(output_dir, filename)
        
        # Use existing save_image util
        if not save_image(image, abs_image_path):
            logging.error("Failed to save drowsiness snapshot")
            return {"saved": False, "error": "Image save failed"}
            
        # Relative path for API/Frontend
        rel_image_path = f"/outputs/events/{filename}"
        
        # 3. Update JSON Log
        json_path = os.path.join(output_dir, "events.json")
        events = []
        
        # Read existing
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    content = f.read()
                    if content.strip():
                        events = json.loads(content)
            except Exception as e:
                logging.warning(f"Could not read existing events.json: {e}")
                events = []
        
        # Append new event
        new_event = {
            "timestamp": timestamp_iso,
            "mode": mode,
            "ear": round(float(ear), 4) if ear else None,
            "status": "DROWSY",
            "image_path": rel_image_path
        }
        events.append(new_event)
        
        # Write back
        with open(json_path, 'w') as f:
            json.dump(events, f, indent=2)
            
        return {
            "saved": True,
            "image_path": rel_image_path,
            "timestamp": timestamp_iso
        }
        
    except Exception as e:
        logging.error(f"Error logging drowsiness event: {e}")
        return {"saved": False, "error": str(e)}
