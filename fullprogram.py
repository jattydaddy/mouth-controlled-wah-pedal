import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mido
from nicegui import ui
import json
import threading

'''
Credits to Theo Barnes for the icon designs. He was commissioned to create masterful pieces using his artistic skill.
'''

# Color variables   
background = "#171516"
buttons = "#1D1B36"
header = "#1D1B36"
ui.colors(primary="#e01a4f") 
ui.query("body").style(f"background-color: {background}") # Set background colour

# Create empty container for all the pages. Has 1 or 3 columns based off screen width
content = ui.element("div").classes("text-white w-full grid grid-cols-1 lg:grid-cols-3")

# Python MIDI
port_name = "pythonmidi 1" # Name of MIDI port set in loopMIDI

# Settings
lip_distance_max = 20 # Max mouth wideness - A lower value means that the CC value reaches 127 with less lip movement
lip_distance_min = 0 # Min mouth wideness - When mouth wideness is lower or equal to this, the CC value is zero
range = lip_distance_max - lip_distance_min # Find range of lip distances

live_percent = {"percentage": 55}

# Function for face tracking and MIDI
def face_tracking():
    base_options = python.BaseOptions(model_asset_path='face_landmarker.task') # Loads the face-tracking model file
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO) # Specifies that the face tracking will be running in video mode

    detector = vision.FaceLandmarker.create_from_options(options)
    cap = cv2.VideoCapture(0) # Starts capturing video from camera

    with mido.open_output(port_name) as port: # Opens the MIDI port
        while cap.isOpened(): # While camera is being captured
            success, frame = cap.read() # Gets frame from camera
            if not success: break # End loop if it fails to grab camera frame 

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) # Format frame of video into a colour format mediapipe can read
            timestamp_ms = int(time.time() * 1000) # Tracks the time the camera has been on
            
            result = detector.detect_for_video(mp_image, timestamp_ms) # Processes the frame, assigning it a timestamp
            lip_distance = 0
            if result.face_landmarks: # If there is a face detected
                landmarks = result.face_landmarks[0] # Gets the landmark data for the face
                
                top_lip = landmarks[13] # The top and bottom lips are number 13 and 14 in the face mesh - give them variable names
                bottom_lip = landmarks[14]

                h, _, _ = frame.shape # Gets height of the video frame
                lip_distance = int(bottom_lip.y * h - top_lip.y * h) # Set variable lip_distance to the distance between the lips

            wah_percent = ((lip_distance - lip_distance_min) / range * 100) # Turn lip distance into a percentage, this will hopefully make it easier to work with later.
            wah_percent = max(0, min(wah_percent, 100)) # Set upper and lower bounds of the percentage number so that it wont go under 0 and over 100

            live_percent["percentage"] = wah_percent

            cc_value = int(127 * (wah_percent / 100))

            port.send(mido.Message('control_change', channel=0, control=11, value=cc_value)) # Sends CC message to CC11(the CC number usually used for expression)
        
            cv2.imshow('Lip Tracker', frame) # Opens a window showing the video frame
            if cv2.waitKey(1) & 0xFF == 27: # Exit loop when escape is pressed
                break

    cap.release()
    cv2.destroyAllWindows()

# Start thread
thread = threading.Thread(target=face_tracking, daemon=True)
thread.start()

# Settings code
settings_file = "settings.json"

 # Function to update the JSON file
def save_settings(wah_min, wah_max):
    # Values of the settings stored in a dictionary
    setting_values = {
        "wah_min": wah_min,
        "wah_max": wah_max
    }

    # Write dictionary into file
    with open(settings_file, "w") as f:
        json.dump(setting_values, f) 

# Load the stored values into variables
def load_settings():    
    # Open JSON file in read mode and get the values in the dictionary.
    with open(settings_file, "r") as f:
        data = json.load(f)
    return {
        "wah_min": data.get("wah_min", 0.0),
        "wah_max": data.get("wah_max", 10.0)
    }

# Variable for the wah gauge
gauge_max = 722
# Gauge function
def gauge(value, gauge_html):
    offset = gauge_max - (gauge_max * (value/100))

    # Creates an SVG gauge
    gauge_html.content =  f'''
      <svg width="250" height="250" viewBox="-31.25 -31.25 312.5 312.5" version="1.1" xmlns="http://www.w3.org/2000/svg" style="transform:rotate(90deg)">
        <circle r="115" cx="125" cy="125" fill="transparent" stroke="#2A274C" stroke-width="40"></circle>
        <circle r="115" cx="125" cy="125" stroke="#e01a4f" stroke-width="40" stroke-linecap="round" stroke-dashoffset="{offset}px" fill="transparent" stroke-dasharray="722.2px"></circle>
        <text x="125" y="140" fill="#e8e8e8" font-size="52px" font-weight="bold" text-anchor="middle" dominant-baseline="central" style="transform:rotate(-90deg); transform-origin: 125px 125px;">{value}</text>
      </svg>
    '''
    gauge_html.update()

# Functions for each page
def home():
    with content:
        title.set_text("Wah") # Changes title

        gauge_html = ui.html().classes("flex justify-center pt-20") # Creates an element for the HTML of the gauge

        ui.timer(0.05, lambda: gauge(live_percent["percentage"], gauge_html))

def calibrate():
    with content:
        title.set_text("Calibrate")
        
def settings(): 
    with content:
        title.set_text("Settings")

        setting_values = load_settings()
    
        ui.label("Wah Minimum").classes("text-xl py-8")
        ui.slider(min=0, max=10, step=0.1, value=setting_values["wah_min"]).props("label-always")\
        .on("change", lambda e: print(e.args))

        ui.label("Wah Maximum").classes("text-xl py-8")
        ui.slider(min=0, max=10, step=0.1, value=setting_values["wah_max"]).props("label-always")\
        .on("change", lambda e: print(e.args))


# Creates header with a title
with ui.header().style(f"background-color: {header}")\
    .classes("rounded-b-3xl h-16"):
    title = ui.label("Wah").classes("text-2xl")

# Footer with 3 column grid. Hide nav bar if screen width is wider than 1024px, so it won't show on a desktop device.
with ui.footer().classes("grid grid-cols-3 h-25 p-0 gap-0 lg:hidden")\
    .style(f"background-color: {background}"):

    # Creates buttons for the spaces in the grid - Each button occupies its respective third of the nav bar
    ui.button("Wah", color=buttons, on_click=home).props("flat")\
        .classes("h-full w-full rounded-none text-white rounded-tl-3xl")
    
    ui.button("Calibrate", color=buttons, on_click=calibrate).props("flat")\
        .classes("h-full w-full rounded-none text-white")

    ui.button("Settings", color=buttons, on_click=settings).props("flat")\
        .classes("h-full w-full rounded-none text-white rounded-tr-3xl")

home() # Make the webapp load into the homepage

ui.run()