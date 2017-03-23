# -*- encoding: UTF-8 -*-

import sys
from naoqi import ALProxy
import time
import almath



def move_head(x,y):
    names = "Head"
    yaw_x = x/160*119.5*almath.TO_RAD
    pitch_y = (y-120)/120*29.5*almath.TO_RAD
    targetAngles      = [yaw_x, pitch_y]
    print(targetAngles)
    print(x/160*119.5, (y-120)/120*29.5)
    maxSpeedFraction  = 0.3 # Using 20% of maximum joint speed
    motionProxy.setAngles(names, targetAngles, maxSpeedFraction)

def main(robotIP):
    

    motionProxy.setStiffnesses("Head", 1.0)

    # Simple command for the HeadYaw joint at 10% max speed
    names            = "HeadYaw"
    angles           = 0.0*almath.TO_RAD
    fractionMaxSpeed = 0.5
##########################################################################    
    motionProxy.setAngles(names,angles,fractionMaxSpeed)
# angles = 30.0*almath.TO_RAD, 30 means the angle to the left. it is concrete angle.
# if it changes to 0, it means move to the center position.
##########################################################################
    time.sleep(3.0)
    #motionProxy.setAngles(names,-120*almath.TO_RAD,fractionMaxSpeed)
    #motionProxy.angleInterpolationWithSpeed(names, -120*almath.TO_RAD, fractionMaxSpeed)
    #move_head(319.0, 1.0)# right, up
    move_head(319.0,239.0)# right, down
    motionProxy.setStiffnesses("Head", 0.0)

if __name__ == "__main__":
    robotIP = "nao.local"
    PORT = 9559

    try:
        motionProxy = ALProxy("ALMotion", robotIP, PORT)
    except Exception,e:
        print "Could not create proxy to ALMotion"
        print "Error was: ",e
        sys.exit(1)

    if len(sys.argv) <= 1:
        print "Usage python almotion_controllingjoints.py robotIP (optional default: 127.0.0.1)"
    else:
        robotIp = sys.argv[1]

    main(robotIP)
