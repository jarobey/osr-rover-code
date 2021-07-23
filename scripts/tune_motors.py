#!/usr/bin/python3

from time import sleep
import sys
from os import path
from roboclaw_3 import Roboclaw

import curses
from curses import wrapper

config_dict = {
    0x0003: {
        0x0000: "RC Mode",
        0x0001: "Analog Mode",
        0x0002: "Simple Serial Mode",
        0x0003: "Packet Serial Mode"
    },
    0x001c: {
        0x0000: "Battery Mode Off",
        0x0004: "Battery Mode Auto",
        0x0008: "Battery Mode 2 Cell",
        0x000C: "Battery Mode 3 Cell",
        0x0010: "Battery Mode 4 Cell",
        0x0014: "Battery Mode 5 Cell",
        0x0018: "Battery Mode 6 Cell",
        0x001C: "Battery Mode 7 Cell",
        0x0020: "Mixing", #?
        0x0040: "Exponential", #?
        0x0080: "MCU" #?
    },
    0x00e0: {
        0x0000: "BaudRate 2400",
        0x0020: "BaudRate 9600",
        0x0040: "BaudRate 19200",
        0x0060: "BaudRate 38400",
        0x0080: "BaudRate 57600",
        0x00A0: "BaudRate 115200",
        0x00C0: "BaudRate 230400",
        0x00E0: "BaudRate 460800",
        0x0100: "FlipSwitch" #?
    },
    0x0700: {
        0x0000: "Packet Address 0x80",
        0x0100: "Packet Address 0x81",
        0x0200: "Packet Address 0x82",
        0x0300: "Packet Address 0x83",
        0x0400: "Packet Address 0x84",
        0x0500: "Packet Address 0x85",
        0x0600: "Packet Address 0x86",
        0x0700: "Packet Address 0x87"
    },
    0x0800: {
        0x0000: None,
        0x0800: "Slave Mode"
    },
    0x1000: {
        0x0000: None,
        0X1000: "Relay Mode"
    },
    0x2000: {
        0x0000: None,
        0x2000: "Swap Encoders"
    },
    0x4000: {
        0x0000: None,
        0x4000: "Swap Buttons"
    },
    0x8000: {
        0x0000: None,
        0x8000: "Multi-Unit Mode"
    }
}

error_dict = {
    0x000000: "Normal",
    0x000001: "E-Stop",
    0x000002: "Temperature Error",
    0x000004: "Temperature 2 Error",
    0x000008: "Main Voltage High Error",
    0x000010: "Logic Voltage High Error",
    0x000020: "Logic Voltage Low Error",
    0x000040: "M1 Driver Fault Error",
    0x000080: "M2 Driver Fault Error",
    0x000100: "M1 Speed Error",
    0x000200: "M2 Speed Error",
    0x000400: "M1 Position Error",
    0x000800: "M2 Position Error",
    0x001000: "M1 Current Error",
    0x002000: "M2 Current Error",
    0x010000: "M1 Over Current Warning",
    0x020000: "M2 Over Current Warning",
    0x040000: "Main Voltage High Warning",
    0x080000: "Main Voltage Low Warning",
    0x100000: "Temperature Warning",
    0x200000: "Temperature 2 Warning",
    0x400000: "S4 Signal Triggered",
    0x800000: "S5 Signal Triggered",
    0x01000000: "Speed Error Limit Warning",
    0x02000000: "Position Error Limit Warning",
}

def printControllers(message, function, action=None):
    print(message)
    for rc in range(128,133):
        print("{} = {}".format(rc, function(rc)))
        if action:
            action(rc)

def decodeConfig(config):
    decoded = []
    for code, settings in config_dict.items():
        masked = config & code
        if settings[masked]:
            decoded.append(settings[masked])
    return decoded

def decodeError(error):
    decoded = []
    for code, message in error_dict.items():
        if code == error: 
            decoded.append(message)
            break
        if code & error:
            decoded.append(message)
    return decoded

if __name__ == "__main__":

    wheel_addresses = [128, 129, 130]
    corner_addresses = [131, 132]
    roboclaw = Roboclaw("/dev/serial0", 115200)
    roboclaw.Open()

    printControllers("Starting encoder modes",roboclaw.ReadEncoderModes)

    # Drive Motors
    roboclaw.SetM1EncoderMode(128,64)
    roboclaw.SetM2EncoderMode(128,64)
    roboclaw.SetM1EncoderMode(129,64)
    roboclaw.SetM2EncoderMode(129,32)
    roboclaw.SetM1EncoderMode(130,32)
    roboclaw.SetM2EncoderMode(130,32)

    # Corner Motors
    roboclaw.SetM1EncoderMode(131,33)
    roboclaw.SetM2EncoderMode(131,33)
    roboclaw.SetM1EncoderMode(132,33)
    roboclaw.SetM2EncoderMode(132,33)

    roboclaw.SetM1PositionPID(131, 8.0, 0.08, 0.04, 0, 0, 246, 1435)
    roboclaw.SetM2PositionPID(131, 8.0, 0.08, 0.04, 0, 0, 245, 1446)
    roboclaw.SetM1PositionPID(132, 8.0, 0.08, 0.04, 0, 0, 383, 1402)
    roboclaw.SetM2PositionPID(132, 8.0, 0.08, 0.04, 0, 0, 347, 1379)

    printControllers("Updated encoder modes",roboclaw.ReadEncoderModes, action=roboclaw.WriteNVM)

    # printControllers("Errors",roboclaw.ReadError)
    print("Decoded errors")
    for rc in range(128,133):
        errors = roboclaw.ReadError(rc)[1]
        print("{} = {} = {}".format(rc, errors, decodeError(errors)))

    # printControllers("Config",roboclaw.GetConfig)
    print("Decoded config")
    for rc in range(128,133):
        config = roboclaw.GetConfig(rc)[1]
        print("{} = {} = {}".format(rc, config, decodeConfig(config)))

    # for rc in range(128,133):
    #     roboclaw.SetLogicVoltages(rc, 55, 340)
    #     roboclaw.SetMainVoltages(rc, 115, 340)

    printControllers("Main Battery", roboclaw.ReadMinMaxMainVoltages)

    printControllers("Logic Battery", roboclaw.ReadMinMaxLogicVoltages, action=roboclaw.WriteNVM)

    # print("Steering encoders")
    # for rc in corner_addresses:
    #     print("Start controller {}".format(rc))
    #     print("{} M1 = {}".format(rc, roboclaw.ReadEncM1(rc)))
    #     print("{} M2 = {}".format(rc, roboclaw.ReadEncM2(rc)))
    #     roboclaw.BackwardM1(rc, 32)
    #     roboclaw.BackwardM2(rc, 32)
    #     sleep(.5)
    #     print("Mid controller {}".format(rc))
    #     print("{} M1 = {}".format(rc, roboclaw.ReadEncM1(rc)))
    #     print("{} M2 = {}".format(rc, roboclaw.ReadEncM2(rc)))
    #     roboclaw.ForwardM1(rc, 32)
    #     roboclaw.ForwardM2(rc, 32)
    #     sleep(.5)
    #     roboclaw.BackwardM1(rc, 0)
    #     roboclaw.BackwardM2(rc, 0)
    #     print("End controller {}".format(rc))
    #     print("{} M1 = {}".format(rc, roboclaw.ReadEncM1(rc)))
    #     print("{} M2 = {}".format(rc, roboclaw.ReadEncM2(rc)))

    # while True:
    #     print("Back Left = {}".format(roboclaw.ReadEncM2(132)))
    #     sleep(.5)
