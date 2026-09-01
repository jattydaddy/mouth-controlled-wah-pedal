import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(model_asset_path='face_landmarker.task') # Loads the face-tracking model file
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO) # Specifies that the face tracking will be running in video mode

detector = vision.FaceLandmarker.create_from_options(options)
cap = cv2.VideoCapture(0) # Starts capturing video from camera

while cap.isOpened(): # While camera is being captured
    success, frame = cap.read() # Gets frame from camera
    if not success: break # End loop if it fails to grab camera frame 

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) # Format frame of video into a colour format mediapipe can read
    timestamp_ms = int(time.time() * 1000) # Tracks the time the camera has been on
    
    result = detector.detect_for_video(mp_image, timestamp_ms) # Processes the frame, assigning it a timestamp

    if result.face_landmarks: # If there is a face detected
        landmarks = result.face_landmarks[0] # Gets the landmark data for the face
        
        top_lip = landmarks[13] # The top and bottom lips are number 13 and 14 in the face mesh - give them variable names
        bottom_lip = landmarks[14]

        h, w, _ = frame.shape # Gets width and height of the video frame
        print(f"Lip Distance: {int(bottom_lip.y * h - top_lip.y * h)}") # Print the distance between the lips

    cv2.imshow('Lip Tracker', frame) # Opens a window showing the camera
    if cv2.waitKey(1) & 0xFF == 27: # Exit loop when escape is pressed
        break

cap.release()
cv2.destroyAllWindows()