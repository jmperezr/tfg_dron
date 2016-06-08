import os
import sys
import time
from dronekit import connect, Command, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import drone
import thread

class proxyDrone():
	def __init__(self, numVehicle, lock):
        	self.waypoint= None
        	self.status= "idle"
		self.numVehicle= numVehicle
		self.lock = lock
		self.vehicle = None
		self.inFlight= False
        	print "Proxy created."

	def takeoff(self, aTargetAltitude):

    		print "Drone %s: Basic pre-arm checks" %self.numVehicle
    		
    		while not self.vehicle.is_armable:
        		print "  Drone %s: Waiting for vehicle to initialise..." %self.numVehicle
        		time.sleep(2)

        
    		print "Drone %s: Arming motors" %self.numVehicle
    		# vehicle Copter must be armed in guided mode
    		self.vehicle.mode    = VehicleMode("GUIDED")
    		self.vehicle.armed   = True    

    		while not self.vehicle.armed:      
        		print "  Drone %s: Waiting for arming..." %self.numVehicle
        		time.sleep(2)

    		print "Drone %s: Takeoff!!" %self.numVehicle
    		self.vehicle.simple_takeoff(aTargetAltitude) 

       		while True:
        		print "Drone %s: Altitude: %s" %(self.numVehicle, self.vehicle.location.global_relative_frame.alt)      
        		if self.vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            			print "Drone %s: Reached target altitude" %self.numVehicle
            			break
        		time.sleep(2)

	def uploadMission(self, land):
		cmds = self.vehicle.commands
		cmds.clear()
		
		if not land:
			cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, float(self.waypoint.lon) , float(self.waypoint.lat), float(self.waypoint.alt)))
			cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, float(self.waypoint.lon) , float(self.waypoint.lat), float(self.waypoint.alt)))
			
			cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, float(self.waypoint.lon) , float(self.waypoint.lat), float(self.waypoint.alt)))

		else:
			cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0))
			cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0,  0, 0, 0))
		
		cmds.upload()

	def connectDrone(self):
		self.lock.acquire()
		instanceDrone = drone.drone(self.numVehicle)
		instanceDrone.startDrone()
		print "Connected to vehicle: %s" % instanceDrone.UdpPort
		self.vehicle= connect("127.0.0.1:%d" % instanceDrone.UdpPort, wait_ready=True, heartbeat_timeout=30)
		self.vehicle.parameters['SYSID_THISMAV']= self.numVehicle + 1
		self.lock.release()
		
		self.takeoff(10)
		self.inFlight = True
		
			
	def doMission(self, land):
		
		self.uploadMission(land)

		print "Drone %s: Starting mission..." %self.numVehicle

		self.vehicle.commands.next=0
	

		self.vehicle.mode = VehicleMode("AUTO")

		while True:
			time.sleep(2)
			nextwaypoint= self.vehicle.commands.next
			
			if not land:
				if nextwaypoint==2: #Dummy waypoint
        				print "Drone %s: Next waypoint..." %self.numVehicle
        				break;
			else:
				if (self.vehicle.location.global_relative_frame.alt <= 0):
            				print "Drone %s: Landing completed" %self.numVehicle
					self.vehicle.close()
            				break
		#self.vehicle.close()
		self.status= "idle"
	
	def insertWaypoints(self, waypoint):
		self.status= "busy"
		self.waypoint= waypoint
		
