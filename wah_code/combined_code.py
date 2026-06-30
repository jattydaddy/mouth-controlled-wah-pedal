import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mido

port_name = 'pythonmidi 1' # Name of MIDI port set in loopMIDI

# Settings
lip_distance_max = 20 # Max mouth wideness - A lower value means that the CC value reaches 127 with less lip movement
lip_distance_min = 0 # Min mouth wideness - When mouth wideness is lower or equal to this, the CC value is zero
range = lip_distance_max - lip_distance_min # Find range of lip distances

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
        lip_distance = int(bottom_lip.y * h - top_lip.y * h) # Set variable lip_distance to the distance between the lips

    percentage = ((lip_distance - lip_distance_min) / range * 100) # Turn lip distance into a percentage, this will hopefully make it easier to work with later.
    percentage = max(0, min(percentage, 100)) # Set upper and lower bounds of the percentage number

    cc_value = int(127 * (percentage / 100))

    with mido.open_output(port_name) as port: # Opens the MIDI port
        port.send(mido.Message('control_change', channel=0, control=11, value=cc_value)) # Sends CC message to CC11(the CC number usually used for expression)
    
    cv2.imshow('Lip Tracker', frame) # Opens a window showing the frame
    if cv2.waitKey(1) & 0xFF == 27: # Exit loop when escape is pressed
        break

cap.release()
cv2.destroyAllWindows()