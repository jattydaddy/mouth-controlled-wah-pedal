import mido

port_name = 'pythonmidi 1' # Name of MIDI port set in loopMIDI

with mido.open_output(port_name) as port: # Opens the MIDI port
    port.send(mido.Message('control_change', channel=0, control=11, value=127)) # Sends CC message to CC11(the CC number usually used for expression)


