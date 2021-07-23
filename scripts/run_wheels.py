#!/usr/bin/python
# A short and sweet script to test communication with a single roboclaw motor controller.
# usage 
#   $ python roboclawtest.py 128

from time import sleep
import sys
from os import path
# need to add the roboclaw.py file in the path
sys.path.append(path.join(path.expanduser('~'), 'osr_ws/src/osr-rover-code/ROS/osr/src'))
from roboclaw import Roboclaw

def displayspeed(roboclaw, address):
    enc1 = roboclaw.ReadEncM1(address)
    enc2 = roboclaw.ReadEncM2(address)
    speed1 = roboclaw.ReadSpeedM1(address)
    speed2 = roboclaw.ReadSpeedM2(address)

    print("Encoder1:"),
    if(enc1[0]==1):
        print enc1[1],
        print format(enc1[2],'02x'),
    else:
        print "failed",
    print "Encoder2:",
    if(enc2[0]==1):
        print enc2[1],
        print format(enc2[2],'02x'),
    else:
        print "failed " ,
    print "Speed1:",
    if(speed1[0]):
        print speed1[1],
    else:
        print "failed",
    print("Speed2:"),
    if(speed2[0]):
        print speed2[1]
    else:
        print "failed "

if __name__ == "__main__":
    
    wheel_rc_addresses = [128, 129, 130]
    roboclaw = Roboclaw("/dev/serial0", 115200)
    roboclaw.Open()

    # Set direction
    roboclaw.SetM1EncoderMode(128,64)
    roboclaw.SetM2EncoderMode(128,64)
    roboclaw.SetM1EncoderMode(129,64)
    roboclaw.SetM2EncoderMode(129,32)
    roboclaw.SetM1EncoderMode(130,32)
    roboclaw.SetM2EncoderMode(130,32)
    
    # Show initial settings
    for rc in wheel_rc_addresses:
        roboclaw.WriteNVM(rc)
        roboclaw.ResetEncoders(rc)
        print "Readings for {}".format(rc)
        print roboclaw.ReadVersion(rc)
        displayspeed(roboclaw, rc)

        roboclaw.ForwardM1(rc, 32)
        roboclaw.ForwardM2(rc, 32)

    sleep(1)

    for rc in wheel_rc_addresses:
        displayspeed(roboclaw, rc)
        roboclaw.ForwardM1(rc, 0)
        roboclaw.ForwardM2(rc, 0)

    sleep(1)

    for rc in wheel_rc_addresses:
        print "Readings for {}".format(rc)
        displayspeed(roboclaw, rc)
        print roboclaw.ReadError(rc)