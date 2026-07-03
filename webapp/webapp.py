from nicegui import ui

'''
Credits to Theo Barnes for the icon designs. He was commissioned to create masterful pieces using his artistic skill.
'''

# Color variables
background = "#171516"
buttons = "#1D1B36"

# Set background color
ui.query('body').style(f'background-color: {background}') # Set background color

# Creates a footer with a 3 column flexbox grid
with ui.footer().classes("grid grid-cols-3 h-25 p-0 gap-0")\
    .style(f"background-color: {background}"):

    # Creates buttons for the spaces in the grid - Each button occupies its respective third of the nav bar
    ui.button("Wah", color=buttons).props('flat')\
        .classes("h-full w-full rounded-none text-white rounded-tl-3xl")
    
    ui.button("Calibrate", color=buttons).props('flat')\
        .classes("h-full w-full rounded-none text-white")

    ui.button("Settings", color=buttons).props('flat')\
        .classes("h-full w-full rounded-none text-white rounded-tr-3xl")

ui.run()