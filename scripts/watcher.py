#!/usr/bin/python3

from time import sleep
import sys
from os import path
from roboclaw_3 import Roboclaw

import curses
from curses import wrapper

from tune_motors import error_dict, config_dict, decodeConfig, decodeError

current_speed = 0
selected_encoder = 0
encoders = None

def init():
    global encoders
    if encoders == None:
        encoders = []
        for rc in motor_addresses:
            # controller, motor, name
            encoders.append([rc, 0, motor_addresses[rc][0]])
            encoders.append([rc, 1, motor_addresses[rc][1]])

def get_selected_encoder():
    return encoders[selected_encoder]

def draw_corners(stdscr, offset_y, offset_x):
    encoders = []
    for rc in motor_addresses:
        encoders.append([motor_addresses[rc][0], roboclaw.ReadEncM1(rc)[1]])
        encoders.append([motor_addresses[rc][1], roboclaw.ReadEncM2(rc)[1]])

    line = 0
    for encoder in encoders:
        fmt = curses.A_STANDOUT if line/2 == selected_encoder else curses.A_NORMAL
        stdscr.addstr(offset_y + line, 5, '{:>15s}: {:6d}'.format(*encoder), fmt)
        line += 2

def draw_selected(stdscr, offset_y, offset_x):
    encoder = get_selected_encoder()
    line = offset_y
    stdscr.addstr(offset_y, offset_x, '{:25s}'.format(encoder[2]))
    line += 2
    stdscr.addstr(line, offset_x, 'Config: {:50s}'.format(','.join(decodeConfig(roboclaw.GetConfig(encoder[0])[1]))))
    line += 2
    stdscr.addstr(line, offset_x, 'Error: {:50s}'.format(','.join(decodeError(roboclaw.ReadError(encoder[0])[1]))))
    line += 2
    stdscr.addstr(line, offset_x, 'Encoder Modes: {}'.format(roboclaw.ReadEncoderModes(encoder[0])[1+encoder[1]]))
    line += 2
    stdscr.addstr(line, offset_x, 'Currents: {}'.format(roboclaw.ReadCurrents(encoder[0])[1+encoder[1]]))
    line += 2

    #Get correct motor functions
    f_speed = None
    f_VelocityPID = None
    f_PositionPID = None
    f_Enc = None

    if encoder[1]:
        f_speed = roboclaw.ReadSpeedM2
        f_VelocityPID = roboclaw.ReadM2VelocityPID
        f_PositionPID = roboclaw.ReadM2PositionPID
        f_Enc = roboclaw.ReadEncM2
    else:
        f_speed = roboclaw.ReadSpeedM1
        f_VelocityPID = roboclaw.ReadM1VelocityPID
        f_PositionPID = roboclaw.ReadM1PositionPID
        f_Enc = roboclaw.ReadEncM1

    stdscr.addstr(line, offset_x, 'Encoder: {:25s}'.format('{}'.format(f_Enc(encoder[0]))))
    line += 2
    stdscr.addstr(line, offset_x, 'Speed: {:25s}'.format('{}'.format(f_speed(encoder[0]))))
    line += 2
    stdscr.addstr(line, offset_x, 'Velocity PID: {:90s}'.format('{}'.format(f_VelocityPID(encoder[0]))))
    line += 2
    stdscr.addstr(line, offset_x, 'Position PID: {:90s}'.format('{}'.format(f_PositionPID(encoder[0]))))
    line += 2

def stop_all():
    global current_speed 
    current_speed = 0
    for rc in motor_addresses:
        roboclaw.ForwardM1(rc,0)
        roboclaw.ForwardM2(rc,0)

def update_speed():
    encoder = get_selected_encoder()
    if current_speed < 0:
        f_speed = roboclaw.BackwardM2 if encoder[1] else roboclaw.BackwardM1
    else:
        f_speed = roboclaw.ForwardM2 if encoder[1] else roboclaw.ForwardM1
    f_speed(encoder[0], abs(current_speed))

def main(stdscr):
    global selected_encoder
    global current_speed

    curses.curs_set(0)
    stdscr.timeout(250)
    stdscr.border(0)
    footer = curses.LINES - 4
    stdscr.addstr(footer, 5, 'Artie motor tuner', curses.A_BOLD)
    stdscr.addstr(footer + 1, 5, 'Press q to close this screen', curses.A_NORMAL)
    val = 1

    while True:
        # Footer
        stdscr.addstr(1,1, "{}".format(val), curses.A_NORMAL)
        val += 1

        # Selector
        draw_corners(stdscr, 3, 5)

        # Selected
        draw_selected(stdscr, 5, 32)

        # Draw
        stdscr.refresh()

        ch = stdscr.getch()
        if ch == ord('q'):
            break
        elif ch == curses.KEY_UP:
            selected_encoder = (selected_encoder - 1) % len(encoders)
            stop_all()
        elif ch == curses.KEY_DOWN:
            selected_encoder = (selected_encoder + 1) % len(encoders)
            stop_all()
        elif ch == ord(' '):
            stop_all()
        elif ch == ord('w'):
            current_speed += 8
            update_speed()
        elif ch == ord('s'):
            current_speed -= 8
            update_speed()
        else:
            if ch:
                stdscr.addch(footer, curses.COLS-8, ch, curses.A_BOLD)

motor_addresses = {
    128: {0: "Drive, FR", 1: "Drive, MR"},
    129: {0: "Drive, RR", 1: "Drive, RL"},
    130: {0: "Drive, ML", 1: "Drive, FL"},
    131: {0: "Steer, FR", 1: "Steer, BR"},
    132: {0: "Steer, BL", 1: "Steer, FL"}
}
roboclaw = Roboclaw("/dev/serial0", 115200)
roboclaw.Open()
init()
wrapper(main)
