#!/usr/bin/env python

"""edgar_tracker.py: Trace the movement of an object to play delightful music"""

__author__ = "Marco Pettorali"
__copyright__ = "Copyright 2020"

import cv2  # for handling images
import click  # for handling CLI parameters
import time  # for handling note duration
import mido  # for handling MIDI connections
from threading import Thread


def scale_builder(keynote_name, octaves, scale):
    keynote = 0
    # extract keynote
    note = list(keynote_name)

    if note[0] == 'C':
        keynote += 0
    if note[0] == 'D':
        keynote += 2
    if note[0] == 'E':
        keynote += 4
    if note[0] == 'F':
        keynote += 5
    if note[0] == 'G':
        keynote += 7
    if note[0] == 'A':
        keynote += 9
    if note[0] == 'B':
        keynote += 11

    if len(note) == 2:
        keynote += (int(note[1]) + 1) * 12
    elif len(note) == 3:
        keynote += (int(note[2]) + 1) * 12
        if note[1] == '#':
            keynote += 1
        else:
            keynote -= 1

    # center keynote
    keynote -= 12*round(octaves/2)

    # scale mapping
    if scale == 'major':
        scale = 'TTSTTTS'
    elif scale == 'minor':
        scale = 'TSTTSTT'
    elif scale == 'hexatonic':
        scale = 'TTTTTT'
    elif scale == 'superlocrian':
        scale = 'STSTTTT'

    ret = [keynote]
    octave_counter = 0
    index = 0
    while octave_counter < octaves:
        if scale[index] == 'T':
            ret.append(ret[-1] + 2)
        else:
            ret.append(ret[-1] + 1)
        index += 1
        if index == len(scale):
            octave_counter += 1
            index = 0
    return ret


class NotePlayer(Thread):
    def __init__(self, port, note, velocity, duration):
        Thread.__init__(self)
        self.port = port
        self.note = note
        self.velocity = velocity
        self.duration = duration

    def run(self):
        msg = mido.Message('note_on', note=self.note, velocity=self.velocity)
        self.port.send(msg)
        time.sleep(self.duration)
        msg = mido.Message('note_off', note=self.note)
        self.port.send(msg)


def take_background_img(camera, bw_threshold):
    # pick the webcam
    cam = cv2.VideoCapture(camera)

    # take the background
    s, background_img = cam.read()

    # convert the picture to greyscale and then to b/w
    background_gray_img = cv2.cvtColor(background_img, cv2.COLOR_BGR2GRAY)
    (thresh, background_bw_img) = cv2.threshold(background_gray_img, bw_threshold, 255, cv2.THRESH_BINARY)
    cv2.imshow('EDGAR Tracker - selected background', background_img)
    cv2.waitKey(1)
    return background_bw_img


def run(background_bw_img, camera, bw_threshold, dot_radius, port_name, note_threshold, keynote, octaves, scale):
    # pick the webcam
    cam = cv2.VideoCapture(camera)

    # open MIDI virtual port
    port = mido.open_output(port_name)

    # create scale
    scale_array = scale_builder(keynote, octaves, scale)

    # previous point
    prev_point_x = 0
    prev_point_y = 0
    while True:
        # take the picture
        s, original_img = cam.read()

        # convert the picture to greyscale and then to b/w
        gray_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
        (thresh, original_bw_img) = cv2.threshold(gray_img, bw_threshold, 255, cv2.THRESH_BINARY)

        # perform the average point
        point_x = 0
        point_y = 0
        points = 0

        for i in range(original_bw_img.shape[0]):  # rows
            for j in range(original_bw_img.shape[1]):  # columns
                original_pixel = original_bw_img[i, j]
                background_pixel = background_bw_img[i, j]
                if original_pixel != background_pixel:
                    point_x += j
                    point_y += i
                    points += 1

        if points != 0:
            point_x = round(point_x / points)
            point_y = round(point_y / points)

        # play the note
        if abs(prev_point_x - point_x) > note_threshold or abs(prev_point_y - point_y) > note_threshold:
            note = NotePlayer(port, scale_array[round(point_x * len(scale_array) / original_bw_img.shape[1])], 60, 1)
            note.start()

        # draw red dot
        original_img[point_y - dot_radius:point_y + dot_radius, point_x - dot_radius:point_x + dot_radius] = [0, 0, 255]

        # draw edited image
        cv2.imshow('EDGAR Tracker', original_img)
        cv2.waitKey(1)

        # exit from app loop when closing the window
        if cv2.getWindowProperty('EDGAR Tracker', 1) == -1:
            break

        prev_point_x = point_x
        prev_point_y = point_y


@click.option('--camera', '-c', default=1, help='set the device id of the camera that you want to use')
@click.option('--bw_threshold', '-b', default=127, help='set the threshold used to recognize moving pixels')
@click.option('--dot_radius', '-d', default=5, help='set the dimension of the dot showing the movement tracker')
@click.option('--port_name', '-p', default='in-port 1', help='choose the name of the virtual port that you want to use')
@click.option('--note_threshold', '-n', default=10, help='set the movement threshold used to trigger notes')
@click.option('--keynote', '-k', default="C4", help='set the key note of the scale')
@click.option('--octaves', '-o', default=3, help='set the number of octaves to be played')
@click.option('--scale', '-s', default='superlocrian',
              help='set the scale (eg. \'TTSTTTS\' or \'major\' for a major scale')
def main(camera, bw_threshold, dot_radius, port_name, note_threshold, keynote, octaves, scale):
    print("+---------------------------------------------+")
    print("+ EDGAR Tracker - movement tracker and player +")
    print("+---------------------------------------------+")
    print()
    input("Press enter to choose the background")
    background_bw_img = take_background_img(camera, bw_threshold)
    input("Press enter to start the tracking")
    run(background_bw_img, camera, bw_threshold, dot_radius, port_name, note_threshold, keynote, octaves, scale)


if __name__ == "__main__":
    main()
