import os
import time
import threading
from dronekit import connect, Command, VehicleMode, LocationGlobalRelative
from xml.etree.ElementTree import ElementTree
import proxyDrone
from threading import Thread
import argparse 
parser = argparse.ArgumentParser(description="Coordinator. Send missions to a certain number of vehicles.")
parser.add_argument("--vehicles", default="1",
                   help="Number of vehicles to which the waypoints are sent. Default 1 vehicle.")
args = parser.parse_args()

class Coordinator():

	def __init__(self, numVehicles):
        	self.waypoints = []
       		self.priority = []
		self.numVehicles = int(numVehicles)
        	print "Coordinator created."

	
	def readXml(self):
		for file in os.listdir("./Waypoints"):
    			if file.endswith(".xml"):
        			print("Reading waypoints of: %s" %file)
				completeName= os.path.abspath("Waypoints/%s" %file)
				xcontent = ElementTree()
    				xcontent.parse(completeName)
    				match= xcontent.findall("waypoint")
				for i in match:
					self.waypoints.append(LocationGlobalRelative(i.find("lat").text, i.find("long").text, i.find("alt").text))
					self.priority.append(i.find("priority").text)

	def waypointsByPriority(self, priority, waypointsTemp):
		try:
			while self.priority:
				index= self.priority.index(str(priority)) 
				self.priority.pop(index)
				waypointsTemp.append(self.waypoints.pop(index))

			self.waypoints= waypointsTemp
		except ValueError:
    			return self.waypointsByPriority(priority+1, waypointsTemp)

	
		
def main():
	coordinator = Coordinator(args.vehicles)
	coordinator.readXml()

	lock = threading.Lock()
	
	coordinator.waypointsByPriority(1, [])
	
	proxy= []
	for i in range(coordinator.numVehicles):
		proxy.append(proxyDrone.proxyDrone(i,lock))
		print i

	#for i in range(len(coordinator.waypoints)):
	#	if(i / coordinator.numVehicles == 0):
	#		proxy[i].insertWaypoints(coordinator.waypoints[i])
	#	else:
	#		remainder = i % coordinator.numVehicles
	#		proxy[remainder].insertWaypoints(coordinator.waypoints[i])
	
	while coordinator.waypoints:
		for i in range(coordinator.numVehicles):	
			if (proxy[i].status == "idle"):
				proxy[i].insertWaypoints(coordinator.waypoints.pop(0))
				proxy[i].doMission(False)			
				#t = threading.Thread(target=proxy[i].doMission)
    				#t.start()

	for i in range(coordinator.numVehicles):
		proxy[i].doMission(True)
	
if __name__ == "__main__":
	main()
