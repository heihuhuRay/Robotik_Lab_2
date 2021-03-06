import cv2
import imutils
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
from naoqi import ALProxy
from vision_definitions import kQVGA,k4VGA,kBGRColorSpace
import almath
# Configuration
NAO="nao.local"
PORT = 9559
robotIP = "nao.local"
try:
    motionProxy = ALProxy("ALMotion", robotIP, PORT)
except Exception,e:
    print "Could not create proxy to ALMotion"
    print "Error was: ",e
    #sys.exit(1)
motionProxy.setStiffnesses("Head", 1.0)
motionProxy.setAngles("Head", [0.0,0.0], 0.2)# Return to (0,0)
# Current cordinates 
X_0 =0  #inital angle of yaw
Y_0 =0  #inital angle of pitch
current_cor = (X_0, Y_0)

# def main(robotIP, head_yaw_angle, head_pitch_angle):
    
#     # Simple command for the HeadYaw joint at 10% max speed
    
#     angles = head_yaw_angle*almath.TO_RAD
    
#     #motionProxy.setAngles(names,angles,fractionMaxSpeed)

#     #motionProxy.setStiffnesses("Head", 0.0)
#     names = "HeadYaw"
#     angleLists = [1.0,-1.0,1.0,-1.0,1.0,0.0]
#     times = [1,3,5,7,9,10]
#     isAbsolute = True
#     motionProxy.angleInterpolation(names, angleLists, times, isAbsolute)

def move_head(a,b):
    names             = "Head"
    yaw_x = a*almath.TO_RAD
    pitch_y = b*almath.TO_RAD
    targetAngles      = [yaw_x, pitch_y]
    maxSpeedFraction  = 0.2 # Using 20% of maximum joint speed
    motionProxy.angleInterpolationWithSpeed(names, targetAngles, maxSpeedFraction)

# Body Stiffness
# def StiffnessOn(proxy):
#     # We use the "Body" name to signify the collection of all joints
#     pNames = "Body"
#     pStiffnessLists = 1.0
#     pTimeLists = 1.0
#     proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)


if __name__=="__main__":    # this is to check if we are importing 
    # Init proxies.
    try:
        motionProxy = ALProxy("ALMotion", robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e

    camera_index=0 # top camera
    (Cordinate_x, Cordinate_y) = (0, 0)# Cordinates of the detected point
    # http://colorizer.org/
    # define the lower and upper boundaries of the "yellow"
    # ball in the HSV color space, then initialize the
    yellowLower = (25, 86, 6)
    yellowUpper = (35, 255, 255)

    redLower = (0,70,50)
    redUpper = (10,255,255)

    greenLower = (100, 53, 185)
    greenUpper = (180, 255, 255)
    # colorLower = yellowLower
    # colorUpper = yellowUpper
    colorLower = redLower
    colorUpper = redUpper
    # Create a proxy for ALVideoDevice
    name="nao_opencv"
    video=ALProxy("ALVideoDevice",NAO,9559)    
    
    # subscribe to video device on a specific camera # BGR for opencv
    name=video.subscribeCamera(name,camera_index,kQVGA,kBGRColorSpace,30) #k4VGA : 1280*960px
    print "subscribed name",name
    
    try: 
        frame=None
        # keep looping
        while True:
            key=cv2.waitKey(33)&0xFF
            if  key == ord('q') or key==27:
                break

            # obtain image
            alimg=video.getImageRemote(name)
            
            # extract fields
            width=alimg[0]
            height=alimg[1]
            nchannels=alimg[2]
            imgbuffer=alimg[6]
                            
            # build opencv image (allocate on first pass)
            if frame is None:
                print 'Grabbed image: ',width,'x',height,' nchannels=',nchannels
                frame=np.asarray(bytearray(imgbuffer), dtype=np.uint8)
                frame=frame.reshape((height,width,3))
            else:
                frame.data=bytearray(imgbuffer)
            
            # Smoothing Images 
            # http://docs.opencv.org/master/d4/d13/tutorial_py_filtering.html#gsc.tab=0 
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            # Converts an image from one color space to another 
            #http://docs.opencv.org/master/df/d9d/tutorial_py_colorspaces.html#gsc.tab=0
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # construct a mask for the color, then perform
            #  a series of dilations and erosions to remove any small
            # blobs left in the mask
            mask = cv2.inRange(hsv, colorLower, colorUpper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None

            # only proceed if at least one contour was found
            if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
#########################################################################################                
                if x>(160+20) and y<(120-20):   # first quadrant 
                    X_0 -= 11.95
                    Y_0 -= 2.95
                    move_head(X_0, Y_0)
                if x<(160-20) and y<(120-20):   # second quadrant
                    X_0 += 11.95
                    Y_0 -= 2.95
                    move_head(X_0, Y_0)
                if x<(160-20) and y>(120+20):   # third quadrant
                    X_0 += 11.95
                    Y_0 += 2.95
                    move_head(X_0, Y_0)
                if x>(160+20) and y>(120+20):   # fourth quadrant
                    X_0 -= 11.95
                    Y_0 += 2.95
                    move_head(X_0, Y_0)
                if (x>140 and x<180) and y<100:   # 5th area
                    Y_0 -= 2.95
                    move_head(X_0, Y_0)
                if (x>140 and x<180) and y>140:   # 7th area
                    Y_0 += 2.95
                    move_head(X_0, Y_0)
                if x<140 and (y>100 and y<140):   # 6th area
                    X_0 += 2.95
                    move_head(X_0, Y_0)
                if x>180 and (y>100 and y<140):   # 8th area
                    X_0 -= 2.95
                    move_head(X_0, Y_0)
#########################################################################################                
                # only proceed if the radius meets a minimum size
                if radius > 10:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                        (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
            # show the frame to our screen
            # Do not run this code if your run your python in the robot 
            # NAO has no screen to show 
            #print((x,y))
            cv2.imshow("Frame", frame)
            #print(x,y) 

    finally: # if anything goes wrong we'll make sure to unsubscribe
        print "unsubscribing",name
        video.unsubscribe(name)
    

