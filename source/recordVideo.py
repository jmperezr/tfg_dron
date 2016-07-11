'''
Keys
----
q - exit
SPACE - screenshot and label detection
'''

import numpy as np
import cv2
import time
import argparse
import base64
import httplib2

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

# The url template to retrieve the discovery document for trusted testers.
DISCOVERY_URL='https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'
 
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
            		photo_file = time.strftime("%d-%m-%Y_%H:%M:%S")+".png"
            		cv2.imwrite(photo_file, frame)
            		print photo_file, 'saved'
			# [START authenticate]
    			credentials = GoogleCredentials.get_application_default()
    			service = discovery.build('vision', 'v1', credentials=credentials, discoveryServiceUrl=DISCOVERY_URL)
    			# [END authenticate]

    			# [START construct_request]
    			with open(photo_file, 'rb') as image:
        			image_content = base64.b64encode(image.read())
        			service_request = service.images().annotate(body={
            				'requests': [{
                				'image': {
                    					'content': image_content.decode('UTF-8')
                				},
                				'features': [{
                    					'type': 'LABEL_DETECTION',
                    					'maxResults': 10
                				}]
            				}]
        			})
        		# [END construct_request]
        
			# [START parse_response]
        		response = service_request.execute()
			size = len(response['responses'][0]['labelAnnotations'])
			for i in range(size):
        			label = response['responses'][0]['labelAnnotations'][i]['description']
				print "Found label: %s" %label
    	else:
        	break

cap.release()
out.release()
cv2.destroyAllWindows()
