import os
import json
import cv2
from datetime import datetime

# Constants
EVENTS_DIR = os.path.join("outputs", "events")
LOG_FILE = os.path.join(EVENTS_DIR, "events.json")

def ensure_event_dirs():
    """
    Ensures that the event output directories exist.
    """
    if not os.path.exists(EVENTS_DIR):
        os.makedirs(EVENTS_DIR, exist_ok=True)

def save_event_snapshot(image_bgr, mode, status):
    """
    Saves the analyzed frame as an image file.
    
    Args:
        image_bgr: The image in BGR format (OpenCV default).
        mode: "webcam" or "image".
        status: "DROWSY" or "NORMAL".
        
    Returns:
        str: Relative path to the saved image (for frontend/logging), or None on failure.
    """
    if image_bgr is None:
        return None
        
    ensure_event_dirs()
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{status.lower()}_{mode}_{timestamp_str}.jpg"
    filepath = os.path.join(EVENTS_DIR, filename)
    
    try:
        success = cv2.imwrite(filepath, image_bgr)
        if success:
            # Return path relative to project root, structured for web access if needed
            # usually clients want /outputs/events/...
            return f"/outputs/events/{filename}"
        return None
    except Exception as e:
        print(f"[EventLogger] Error saving snapshot: {e}")
        return None

def append_event_log(event_dict):
    """
    Appends a new event entry to the JSON log file.
    
    Args:
        event_dict: Dictionary containing event details.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    ensure_event_dirs()
    
    logs = []
    
    # Read existing logs
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                content = f.read()
                if content.strip():
                    logs = json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[EventLogger] Error reading log file: {e}")
            # Start fresh if corrupted
            logs = []
            
    # Append new event
    logs.append(event_dict)
    
    # Write back
    try:
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=4)
        return True
    except IOError as e:
        print(f"[EventLogger] Error writing log file: {e}")
        return False

def save_event(mode, status, ear_value, image_bgr):
    """
    High-level function to handle the full event logging process.
    
    Args:
        mode: "webcam" or "image".
        status: "DROWSY" or "NORMAL" (usually DROWSY for events).
        ear_value: float EAR value.
        image_bgr: The image frame.
        
    Returns:
        dict: Result with 'success', 'timestamp', and 'snapshot_path'.
    """
    timestamp_iso = datetime.now().isoformat()
    
    # 1. Save Snapshot
    snapshot_path = save_event_snapshot(image_bgr, mode, status)
    
    if not snapshot_path:
        return {
            "success": False, 
            "error": "Failed to save snapshot",
            "timestamp": timestamp_iso
        }
    
    # 2. Prepare Log Entry
    event_entry = {
        "timestamp": timestamp_iso,
        "mode": mode,
        "ear_value": float(ear_value) if ear_value is not None else None,
        "status": status,
        "snapshot_path": snapshot_path
    }
    
    # 3. Append to JSON
    log_success = append_event_log(event_entry)
    
    return {
        "success": log_success,
        "timestamp": timestamp_iso,
        "snapshot_path": snapshot_path
    }
