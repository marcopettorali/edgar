#!/usr/bin/env python

"""edgar_tracker_gui.py: GUI for edgar_tracker.py"""

__author__ = "Marco Pettorali"
__copyright__ = "Copyright 2020"

from tkinter import *
from tkinter.ttk import Separator

import mido
import edgar_tracker

# global parameters
port_name = ""
camera = ""
bw_threshold = ""
dot_radius = ""
note_threshold = ""
keynote = ""
octaves = ""
scale = ""
background_bw_img = ''
background_taken = False

# log variable
log = ""

# row counter
counter = 0


def build_output_port(window):
    global port_name, counter
    lbl = Label(window, text="Set output port")
    lbl.grid(column=0, row=counter)
    output_port_menu_options = []
    for str in mido.get_output_names():
        output_port_menu_options.append(str)
    port_name = StringVar(window)
    port_name.set(output_port_menu_options[0])
    output_port_menu = OptionMenu(window, port_name, *output_port_menu_options)
    output_port_menu.grid(column=1, row=counter)
    counter += 1


def build_camera(window):
    global camera, counter
    lbl = Label(window, text="Set camera id")
    lbl.grid(column=0, row=counter)
    camera = StringVar(window)
    camera.set("0")
    camera_entry = Entry(window, textvariable=camera)
    camera_entry.grid(column=1, row=counter)
    counter += 1


def build_bw_threshold(window):
    global bw_threshold, counter
    lbl = Label(window, text="Set black&white threshold")
    lbl.grid(column=0, row=counter)
    bw_threshold = StringVar(window)
    bw_threshold.set("127")
    bw_threshold_entry = Entry(window, textvariable=bw_threshold)
    bw_threshold_entry.grid(column=1, row=counter)
    counter += 1


def build_dot_radius(window):
    global dot_radius, counter
    lbl = Label(window, text="Set tracking dot radius")
    lbl.grid(column=0, row=counter)
    dot_radius = StringVar(window)
    dot_radius.set("5")
    dot_radius_entry = Entry(window, textvariable=dot_radius)
    dot_radius_entry.grid(column=1, row=counter)
    counter += 1


def build_note_threshold(window):
    global note_threshold, counter
    lbl = Label(window, text="Set note trigger threshold")
    lbl.grid(column=0, row=counter)
    note_threshold = StringVar(window)
    note_threshold.set("10")
    note_threshold_entry = Entry(window, textvariable=note_threshold)
    note_threshold_entry.grid(column=1, row=counter)
    counter += 1


def build_keynote(window):
    global keynote, counter
    lbl = Label(window, text="Set central keynote")
    lbl.grid(column=0, row=counter)
    keynote = StringVar(window)
    keynote.set("C4")
    keynote_entry = Entry(window, textvariable=keynote)
    keynote_entry.grid(column=1, row=counter)
    counter += 1


def build_octaves(window):
    global octaves, counter
    lbl = Label(window, text="Set max number of octaves")
    lbl.grid(column=0, row=counter)
    octaves = StringVar(window)
    octaves.set("3")
    octaves_entry = Entry(window, textvariable=octaves)
    octaves_entry.grid(column=1, row=counter)
    counter += 1


def build_scale(window):
    global scale, counter
    lbl = Label(window, text="Set scale")
    lbl.grid(column=0, row=counter)
    scale = StringVar(window)
    scale.set("major")
    scale_entry = Entry(window, textvariable=scale)
    scale_entry.grid(column=1, row=counter)
    counter += 1


def build_log(window):
    global log, counter
    log = StringVar(window)
    log.set("")
    lbl = Label(window, textvariable=log)
    lbl.grid(column=0, row=counter)
    counter += 1


def start(window):
    global background_taken
    if not background_taken:
        log.set("Error: take the background first!")
        return
    if port_name.get() == '' or camera.get() == '' or bw_threshold.get() == '' or dot_radius.get() == '' or note_threshold.get() == '' or keynote.get() == '' or octaves.get() == '' or scale.get() == '':
        log.set("Error: one or more fields are empty")
    window.destroy()

    edgar_tracker.run(background_bw_img, int(camera.get()), int(bw_threshold.get()), int(dot_radius.get()),
                      port_name.get(),
                      int(note_threshold.get()), keynote.get(), int(octaves.get()), scale.get())


def build_start_button(window):
    global camera, counter
    btn = Button(window, text="Start EDGAR Tracker", command=lambda: start(window))
    btn.grid(column=0, row=counter)
    counter += 1


def take_background():
    global background_bw_img, background_taken
    background_bw_img = edgar_tracker.take_background_img(int(camera.get()), int(bw_threshold.get()))
    background_taken = True


def build_take_background_button(window):
    global camera, background_bw_img, counter
    btn = Button(window, text="Take background image", command=take_background)
    btn.grid(column=0, row=counter)
    counter += 1


def build_separator(window):
    global counter
    Separator(window, orient="horizontal").grid(row=counter, sticky="ew")
    counter += 1


def main():
    window = Tk()
    window.title("EDGAR Tracker GUI")
    window.resizable(False, False)

    build_output_port(window)
    build_camera(window)

    build_separator(window)

    build_keynote(window)
    build_octaves(window)
    build_scale(window)

    build_separator(window)

    build_note_threshold(window)
    build_bw_threshold(window)
    build_dot_radius(window)

    build_take_background_button(window)
    build_start_button(window)
    build_log(window)

    window.mainloop()


if __name__ == '__main__':
    main()
