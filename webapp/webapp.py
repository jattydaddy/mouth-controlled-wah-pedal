from nicegui import ui

with ui.footer():
    with ui.tabs().classes("w-full") as tabs:
        home = ui.tab("Home")
        calibrate = ui.tab("Calibrate")
        settings = ui.tab("Settings")

with ui.tab_panels(tabs, value=home).classes('w-full'):
    with ui.tab_panel(home):
        ui.label("home test")
    with ui.tab_panel(calibrate):
        ui.label("calibrate test")
    with ui.tab_panel(settings):
        ui.label("settings test")

ui.run()

    