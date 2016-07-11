'''
Keys
----
q - exit
SPACE - screenshot
'''

import numpy as np
import cv2
import time


print __doc__

number = 0
cap = None
while (True):

        capAux = cv2.VideoCapture(number)
        if not (capAux.isOpened()):
        	break;
     	else:
            number= number+1
            capAux.release()

if (number > 1):   
	cap = cv2.VideoCapture(0)
else:
	cap = cv2.VideoCapture(1)

w=int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
h=int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

# video recorder
fourcc = cv2.cv.CV_FOURCC(*'XVID')
out = cv2.VideoWriter(time.strftime("%d-%m-%Y_%H:%M:%S")+".avi", fourcc, 25, (w, h))

while(cap.isOpened()):
	ch = 0xFF & cv2.waitKey(1)
	ret, frame = cap.read()
	if ret==True:
		out.write(frame)
        	cv2.imshow('frame',frame)
        	if ch == ord('q'):
            		break
		if ch == ord(' '):
            		fn = time.strftime("%d-%m-%Y_%H:%M:%S")+".png"
            		cv2.imwrite(fn, frame)
            		print fn, 'saved'
    	else:
        	break

cap.release()
out.release()
cv2.destroyAllWindows()
