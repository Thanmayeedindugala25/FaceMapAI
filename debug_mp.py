import mediapipe as mp
print(f"File: {mp.__file__}")
try:
    import mediapipe.python.solutions as solutions
    print("Imported mediapipe.python.solutions")
    print(dir(solutions))
except ImportError as e:
    print(f"Failed to import mediapipe.python.solutions: {e}")

try:
    from mediapipe import solutions
    print("From mediapipe import solutions success")
except ImportError as e:
    print(f"From mediapipe import solutions failed: {e}")
