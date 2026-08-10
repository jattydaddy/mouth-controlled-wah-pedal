from nicegui import ui
import json

'''
Credits to Theo Barnes for the icon designs. He was commissioned to create masterful pieces using his artistic skill.
'''

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

# Color variables
background = "#171516"
buttons = "#1D1B36"
header = "#1D1B36"
ui.colors(primary="#e01a4f") 
ui.query("body").style(f"background-color: {background}") # Set background colour

# Create empty container for all the pages
content = ui.element("div").classes("text-white w-full")

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

# Functions for each page
def home():
    content.clear() # Clears what was previously on screen
    with content:
        title.set_text("Wah") # Changes title

        gauge_html = ui.html().classes("flex justify-center pt-20") # Creates an element for the HTML of the gauge
        value = 55
        gauge(value, gauge_html)

def calibrate():
    content.clear()
    with content:
        title.set_text("Calibrate")
        
def settings(): 
    content.clear()
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

# Creates a footer with a 3 column grid
with ui.footer().classes("grid grid-cols-3 h-25 p-0 gap-0")\
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