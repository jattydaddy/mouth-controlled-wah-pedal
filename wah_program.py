import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mido
from nicegui import ui
import json
import os

'''
Credits to Theo Barnes for the icon designs. He was commissioned to create masterful pieces using his artistic skill.
'''

# Color variables   
background = "#171516"
buttons = "#1D1B36"
text_box = "#1D1B36"
header = "#1D1B36"
gauge_color = "#e01a4f"
ui.colors(primary="#e01a4f") 
ui.query("body").style(f"background-color: {background}") # Set background colour

# Create the container for the loading screen. Making sure that it will be displayed on top of every other element
loading_screen = ui.column().classes(f"fixed inset-0 z-100 bg-[{background}] flex items-center justify-center")
# Loading icon and text
with loading_screen:
    ui.spinner("dots", size="lg", color="primary")
    ui.label("Loading Wah...").classes("text-white text-lg font-bold mt-4")
# Deletes the loading acreen container after enough time has passed for the Wah to fully load
ui.timer(4, loading_screen.delete, once=True)

# Fix for error button and text contrast plus loading screen icon
ui.add_head_html('''
    <style>
        .q-notification__actions .q-btn {
            color: #FFFFFF !important;
            font-weight: bold !important;
        }
    </style>
''')

# Create empty container for all the pages. Has 1 or 3 columns based off screen width
content = ui.element("div").classes("text-white w-full grid grid-cols-1 lg:grid-cols-3 gap-4")

# Settings code
settings_file = "settings.json"
default_settings = {"min": 0.0, "max": 50.0}
 # Function to update the JSON file
def save_settings(wah_min, wah_max):
    wah_min = round(wah_min, 1)
    wah_max = round(wah_max, 1)
    # Update new settings for face tracking code
    global lip_distance_min, lip_distance_max
    lip_distance_min = wah_min
    lip_distance_max = wah_max

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
    # Use default values if no settings file is found   
    if not os.path.exists(settings_file):
        return {"wah_min": default_settings["min"], "wah_max": default_settings["max"]}

    # Open JSON file in read mode and get the values in the dictionary.
    with open(settings_file, "r") as f:
        data = json.load(f)
    return {
        "wah_min": data.get("wah_min", default_settings["min"]),
        "wah_max": data.get("wah_max", default_settings["max"])
    }

# Load settings on startup
initial_settings = load_settings()
lip_distance_min = initial_settings["wah_min"]
lip_distance_max = initial_settings["wah_max"]

port_name = "pythonmidi 1" # Name of MIDI port set in loopMIDI

# Updating variables
live_percent = {"percentage":0}
current_lip_distance = {"distance": 0}
midi_error = None

# Initialise face tracking
base_options = python.BaseOptions(model_asset_path='face_landmarker.task') # Loads the face-tracking model file
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO) # Specifies that the face tracking will be running in video mode

detector = vision.FaceLandmarker.create_from_options(options)
cap = cv2.VideoCapture(0) # Starts capturing video from camera

port = None

# Processes the camera frame and sends MIDI command at 30 FPS
def process_frame():
    global port, midi_error
    success, frame = cap.read() # Gets frame from camera
    if not success: return # Return nothing if it fails to grab camera frame 

    if port == None:
        try:
            port = mido.open_output(port_name)
            midi_error = None
        except Exception:
            midi_error = f"Could not open MIDI port {port_name}"

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) # Format frame of video into a colour format mediapipe can read
    timestamp_ms = int(time.time() * 1000) # Tracks the time the camera has been on
    
    result = detector.detect_for_video(mp_image, timestamp_ms) # Processes the frame, assigning it a timestamp
    lip_distance = 0
    if result.face_landmarks: # If there is a face detected
        landmarks = result.face_landmarks[0] # Gets the landmark data for the face
        
        top_lip = landmarks[13] # The top and bottom lips are number 13 and 14 in the face mesh - give them variable names
        bottom_lip = landmarks[14]

        h, _, _ = frame.shape # Gets height of the video frame
        lip_distance = (bottom_lip.y - top_lip.y) * h # Set variable lip_distance to the distance between the lips

    current_lip_distance["distance"] = lip_distance

    range = lip_distance_max - lip_distance_min # Find range of lip distances
    wah_percent = ((lip_distance - lip_distance_min) / range * 100) # Turn lip distance into a percentage, this will hopefully make it easier to work with later.
    wah_percent = max(0, min(wah_percent, 100)) # Set upper and lower bounds of the percentage number so that it wont go under 0 and over 100

    live_percent["percentage"] = wah_percent # Mutates dictionary so gauge can update according to this percentage value

    cc_value = int(127 * (wah_percent / 100)) # Convert percentage to a value from 0 to 127
    if port:
        try:
            port.send(mido.Message('control_change', channel=0, control=11, value=cc_value)) # Sends CC message to CC11(the CC number usually used for expression)
            midi_error = None
        except Exception:
            port = None
            midi_error = f"Could not open MIDI port {port_name}"
ui.timer(0.033, process_frame)

# Gauge code
gauge_max = 722
def gauge(value, gauge_html):
    offset = gauge_max - (gauge_max * (value/100))

    value = round(value)

    # Creates an SVG gauge
    gauge_html.content =  f'''
      <svg width="250" height="250" viewBox="-31.25 -31.25 312.5 312.5" version="1.1" xmlns="http://www.w3.org/2000/svg" style="transform:rotate(90deg)">
        <circle r="115" cx="125" cy="125" fill="transparent" stroke="#2A274C" stroke-width="40"></circle>
        <circle r="115" cx="125" cy="125" stroke="{gauge_color}" stroke-width="40" stroke-linecap="round" stroke-dashoffset="{offset}px" fill="transparent" stroke-dasharray="722.2px"></circle>
        <text x="125" y="140" fill="#e8e8e8" font-size="52px" font-weight="bold" text-anchor="middle" dominant-baseline="central" style="transform:rotate(-90deg); transform-origin: 125px 125px;">{value}</text>
      
        <text x="125" y="165" fill="#9ca3af" font-size="18" text-anchor="middle" transform="rotate(-90 125 125)">Wah %</text>
      </svg>
    '''
    gauge_html.update()

# Functions for each page
def wah_content():
    gauge_html = ui.html().classes("flex justify-center pt-20") # Creates an element for the HTML of the gauge

    # Updates gauge with new value
    def update_gauge():
        gauge(live_percent["percentage"], gauge_html)
    ui.timer(0.05, update_gauge)

    ui.label("Gauge displays the position of the Wah pedal in percentage.\n\nOne hundred means Wah is fully open.\nZero Means Wah is fully closed.") \
        .style(f"background-color: {text_box};") \
        .classes("text-base rounded-lg shadow-md p-4 mt-8 whitespace-pre-line")

def calibrate_content():
    ui.label("To calibrate:\n\n1. Close your mouth and press button one\n\n2. Open your mouth to a comfortable level and press button two") \
        .style(f"background-color: {text_box};") \
        .classes("text-base rounded-lg shadow-md p-4 mt-8 whitespace-pre-line")

    # Saves values and updates sliders with newly calibrated values
    def update_slider_min():
        save_settings(current_lip_distance["distance"], lip_distance_max)
        if min_slider:
            min_slider.value = round(current_lip_distance["distance"], 1)
    def update_slider_max():
        save_settings(lip_distance_min, current_lip_distance["distance"])
        if max_slider:
            max_slider.value = round(current_lip_distance["distance"], 1)

    # Calibrate buttons
    with ui.column().classes("w-full items-center pt-10"):
        ui.button("1. Capture Closed Mouth", on_click=update_slider_min).classes("h-12")
        ui.button("2. Capture Open Mouth", on_click=update_slider_max).classes("h-12")
        
def settings_content(): 
    global min_slider, max_slider
    setting_values = load_settings()

    ui.label("The sliders determine the range of motion of the mouth detection.\n" \
    "A lower Wah Maximum setting will fully open the Wah with less mouth movement.\n" \
    "A higher Wah Minimum setting will fully close the Wah without needing your mouth to be closed") \
        .style(f"background-color: {text_box};") \
        .classes("text-base rounded-lg shadow-md p-4 mt-8 whitespace-pre-line")


    ui.label("Wah Minimum").classes("text-xl py-8")
    min_slider = ui.slider(min=0, max=50, step=0.1, value=setting_values["wah_min"]).props("label-always")

    ui.label("Wah Maximum").classes("text-xl py-8")
    max_slider = ui.slider(min=0, max=50, step=0.1, value=setting_values["wah_max"]).props("label-always")

    # Saves slider values
    def update_json():
        save_settings(min_slider.value, max_slider.value)

    min_slider.on("change", update_json)
    max_slider.on("change", update_json)

# Creates header with a title
with ui.header().style(f"background-color: {header}")\
    .classes("rounded-b-3xl h-16 lg:hidden"):
    title = ui.label("Wah").classes("text-2xl")

# Render all pages. If screen is wider than 1024px, it will override the visibility settings and display all tabs on the same page
with content:
    with ui.element("div").classes("w-full lg:block!") as wah_page:
        wah_content()

    with ui.element("div").classes("w-full lg:block!") as calibrate_page:
        calibrate_content()

    with ui.element("div").classes("w-full lg:block!") as settings_page:
        settings_content()

# Hide or unhide pages according to which button user taps
def show_wah():
    title.set_text("Wah")
    wah_page.set_visibility(True)
    calibrate_page.set_visibility(False)
    settings_page.set_visibility(False)
def show_calibrate():
    title.set_text("Calibrate")
    wah_page.set_visibility(False)
    calibrate_page.set_visibility(True)
    settings_page.set_visibility(False)
def show_settings():
    title.set_text("Settings")
    wah_page.set_visibility(False)
    calibrate_page.set_visibility(False)
    settings_page.set_visibility(True)

# Footer with 3 column grid. Hide nav bar if screen width is wider than 1024px, so it won't show on a desktop device.
with ui.footer().classes("grid grid-cols-3 h-25 p-0 gap-0 lg:hidden")\
    .style(f"background-color: {background}"):

    # Creates buttons for the spaces in the grid - Each button occupies its respective third of the nav bar
    ui.button("Wah", color=buttons, on_click=show_wah).props("flat")\
        .classes("h-full w-full rounded-none text-white rounded-tl-3xl")
    
    ui.button("Calibrate", color=buttons, on_click=show_calibrate).props("flat")\
        .classes("h-full w-full rounded-none text-white")

    ui.button("Settings", color=buttons, on_click=show_settings).props("flat")\
        .classes("h-full w-full rounded-none text-white rounded-tr-3xl")


show_wah()

# Status of the error, used to stop the error message from being spammed by the timer
error_active = None
def check_midi():
    global error_active
    # Check if there is a MIDI error and that it hasn't been shown to the user yet
    if midi_error and midi_error != error_active:
        ui.notify(midi_error, type="negative", position="top", close_button=True, timeout=0, icon="warning")
        error_active = midi_error
    # Reset error status
    elif not midi_error:
        error_active = None

# Loop to check for MIDI errors
ui.timer(1, check_midi)

ui.run()