import time
import threading
import XMLParser
import proxyDrone
from threading import Thread
import argparse 
parser = argparse.ArgumentParser(description="Coordinator. Send missions to a certain number of vehicles.")
parser.add_argument("--vehicles", default="1",
                   help="Number of vehicles simulated to fly to a waypoint. Default 1 vehicle.")
parser.add_argument("--secondWait", default="10",
                   help="Number of seconds the vehicle is stopped on the waypoint. Default 10 seconds.")
parser.add_argument("--secondsPerPhoto", default="10",
                   help="Number of seconds between photo and photo. Default 10 seconds.")
args = parser.parse_args()

class Coordinator():

	def __init__(self, numVehicles, secondWait, secondsPerPhoto):
		self.numVehicles = int(numVehicles)
		self.secondWait = int(secondWait)
		self.secondsPerPhoto = int(secondsPerPhoto)
        	print "Coordinator created."

	def waypointsByPriority(self, priorityIndex, waypoints, priorityWaypoints, waypointsTemp):
		try:
			while priorityWaypoints:
				index = priorityWaypoints.index(str(priorityIndex)) 
				priorityWaypoints.pop(index)
				waypointsTemp.append(waypoints.pop(index))

			waypoints= waypointsTemp
			return waypoints
		except ValueError:
    			return self.waypointsByPriority(priorityIndex+1, waypoints, priorityWaypoints, waypointsTemp)
		
def main():
        try:
		coordinator = Coordinator(args.vehicles, args.secondWait, args.secondsPerPhoto)
		xmlparser = XMLParser.XMLParser()
		xmlparser.readXml()
	
		lock = threading.Lock()
	
		xmlparser.waypoints = coordinator.waypointsByPriority(1, xmlparser.waypoints, xmlparser.priority, [])
	
		proxy= []

		for i in range(coordinator.numVehicles):
			proxy.append(proxyDrone.proxyDrone(i,lock))
			t = threading.Thread(target=proxy[i].connectDrone, args=(coordinator.secondsPerPhoto,))
			t.start()
		
		while xmlparser.waypoints:
			for i in range(coordinator.numVehicles):
				if proxy[i].status == "idle" and proxy[i].inFlight:
					proxy[i].insertWaypoints(xmlparser.waypoints.pop(0))
					t = threading.Thread(target=proxy[i].doMission, args=(False, coordinator.secondWait,))
					t.daemon = True
					t.start()
	
		for i in range(coordinator.numVehicles):
			t = threading.Thread(target=proxy[i].doMission, args=(True, coordinator.secondWait,))
			t.start()
	except (KeyboardInterrupt, SystemExit):
		exit()

if __name__ == "__main__":
	main()
