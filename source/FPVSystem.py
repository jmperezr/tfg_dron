import numpy as np
import cv2
import time
import argparse
import base64
import httplib2
import time
import os

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

class FPVSystem:
	def __init__(self, secondsPerPhoto, numVehicle):
        	self.secondsPerPhoto = secondsPerPhoto
		self.cap = None
		self.out = None
		self.numVehicle = numVehicle
		self.stopVideoCapture = False
		# The url template to retrieve the discovery document for trusted testers.
		self.DISCOVERY_URL = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'
		# [START authenticate]
		self.credentials = GoogleCredentials.get_application_default()
		self.service = discovery.build('vision', 'v1', credentials = self.credentials, discoveryServiceUrl = self.DISCOVERY_URL)
		# [END authenticate]
        	print (chr(27) + "[0;32m" + "FPV System initiated."), ; print (chr(27) + "[0m")	 

	def videoCapture(self):
		number = 0
		cv2.namedWindow("Drone %s" %self.numVehicle, cv2.cv.CV_WINDOW_NORMAL)
		cv2.cv.ResizeWindow("Drone %s" %self.numVehicle, 640, 480)
		cv2.startWindowThread()
		#while True:
        	#	capAux = cv2.VideoCapture(number)
        	#	if not (capAux.isOpened()):
        	#		break;
     		#	else:
            	#		number= number+1
            	#		capAux.release()
		
		#if number > 1:   
		#	self.cap = cv2.VideoCapture(1)
		#else:
		#	self.cap = cv2.VideoCapture(0)
		
		if self.numVehicle == 0:
			self.cap = cv2.VideoCapture('/home/juanma/Escritorio/VideosGoPro/GOPR0293.MP4')
		else:
			self.cap = cv2.VideoCapture('/home/juanma/Escritorio/VideosGoPro/GOPR0293.MP4')

		w = int(self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
		h = int(self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

		# video recorder
		fourcc = cv2.cv.CV_FOURCC(*'XVID')
		self.out = cv2.VideoWriter(time.strftime("Videos/%d-%m-%Y_%H:%M:%S")+".avi", fourcc, 25, (w, h))

		if not self.cap.isOpened():
			print chr(27) + "[0;31m" + "FPV system not connected.", ; print chr(27) + "[0m"

		#cv2.cv.startWindowThread()
		t0 = time.time()
		result= ["Label not found"]

		while self.cap.isOpened() and not self.stopVideoCapture:
			coordY= 30
			ch = 0xFF & cv2.waitKey(1)
			ret, frame = self.cap.read()
			if ret == True:
				for i in result: 
					cv2.putText(frame, i, (20, coordY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
					coordY = coordY + 20

				self.out.write(frame)
        			cv2.imshow("Drone %s" %self.numVehicle,frame)

				timer = round((time.time() - t0) % self.secondsPerPhoto, 2)
				if  timer >= 0 and timer <= 0.99:
            				photoFile = time.strftime("Images/%d-%m-%Y_%H:%M:%S")+".jpg"
            				cv2.imwrite(photoFile, frame)
            				print chr(27) + "[1;33m" + "Drone %s: " %self.numVehicle + photoFile, "saved", ; print chr(27) + "[0m"
					result = self.labelDetection(photoFile, result)	
    			else:
        			break

		self.cap.release()
		self.out.release()
		cv2.destroyWindow("Drone %s" %self.numVehicle)	
		cv2.waitKey(1)
		cv2.waitKey(1)
		cv2.waitKey(1)
		cv2.waitKey(1)
					
	def labelDetection(self, photoFile, result):
    		# [START construct_request]
    		with open(photoFile, 'rb') as image:
        		image_content = base64.b64encode(image.read())
        		service_request = self.service.images().annotate(body = {
            			'requests': [{
                			'image': {
                    				'content': image_content.decode('UTF-8')
                			},
                			'features': [{
                    				'type': 'LABEL_DETECTION',
                    				'maxResults': 5
                			}]
            			}]
        		})
        	# [END construct_request]
        
		# [START parse_response]
        	response = service_request.execute()
		responseLength = len(response['responses'][0])
		if responseLength == 0:
			result = ["Label not found"]
		else:
			labelLength = len(response['responses'][0]['labelAnnotations'])
			result= []
			for i in range(labelLength):
        			label = response['responses'][0]['labelAnnotations'][i]['description']
				result.append(label)
				
		return result
def main():
	fpv = FPVSystem(4)
	fpv.videoCapture()

if __name__ == "__main__":
	main()
