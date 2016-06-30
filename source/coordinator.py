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
                   help="Number of vehicles simulated to fly to a waypoint. Default 1 vehicle.")
parser.add_argument("--wait", default="10",
                   help="Number of seconds the vehicle is stopped on the waypoint. Default 10 seconds.")
args = parser.parse_args()

class Coordinator():

	def __init__(self, numVehicles, waitWaypoint):
        	self.waypoints = []
       		self.priority = []
		self.numVehicles = int(numVehicles)
		self.waitWaypoint = int(waitWaypoint)
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
	coordinator = Coordinator(args.vehicles, args.wait)
	coordinator.readXml()

	lock = threading.Lock()
	
	coordinator.waypointsByPriority(1, [])
	
	proxy= []
	for i in range(coordinator.numVehicles):
		proxy.append(proxyDrone.proxyDrone(i,lock))
		t = threading.Thread(target=proxy[i].connectDrone)
		t.start()
		print i
			
	#Pausa para ajustar pruebas de video
	#try:
    	#	input("Press enter to continue")
	#except SyntaxError:
    	#	pass
	
	while coordinator.waypoints:
		for i in range(coordinator.numVehicles):
			if proxy[i].status == "idle" and proxy[i].inFlight:
				proxy[i].insertWaypoints(coordinator.waypoints.pop(0))
				t = threading.Thread(target=proxy[i].doMission, args=(False, coordinator.waitWaypoint))
				t.start()

	for i in range(coordinator.numVehicles):
		t = threading.Thread(target=proxy[i].doMission, args=(True, coordinator.waitWaypoint))
		t.start()

if __name__ == "__main__":
	main()
