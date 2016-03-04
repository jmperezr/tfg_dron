import os
import sys
import time
from dronekit import connect, Command, VehicleMode
from pymavlink import mavutil
import drone
import thread

class proxyDrone():
	def __init__(self, vehicle, lock):
        	self.waypoints= []
        	self.status= "Idle"
		self.vehicle= vehicle
		self.lock = lock
        	print "Proxy created."

	def takeoff(self, vehicle, aTargetAltitude):

    		print "Drone %s: Basic pre-arm checks" %self.vehicle
    		
    		while not vehicle.is_armable:
        		print "  Drone %s: Waiting for vehicle to initialise..." %self.vehicle
        		time.sleep(2)

        
    		print "Drone %s: Arming motors" %self.vehicle
    		# vehicle Copter debe ser armado en modo GUIADO
    		vehicle.mode    = VehicleMode("GUIDED")
    		vehicle.armed   = True    

    		while not vehicle.armed:      
        		print "  Drone %s: Waiting for arming..." %self.vehicle
        		time.sleep(2)

    		print "Drone %s: Takeoff!!" %self.vehicle
    		vehicle.simple_takeoff(aTargetAltitude) 

       		while True:
        		print "Drone %s: Altitude: %s" %(self.vehicle, vehicle.location.global_relative_frame.alt)      
        		if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            			print "Drone %s: Reached target altitude" %self.vehicle
            			break
        		time.sleep(2)

	def uploadMission(self, vehicle):
		cmds = vehicle.commands
		cmd=Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 32.8351736920028898, -117.162837982177734, 0)
		cmds.add(cmd)
		
		for i in self.waypoints:
			cmd=Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, float(i.lon) , float(i.lat), float(i.alt))
			cmds.add(cmd)
		cmd1=Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0)
		cmd2=Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0,  0, 0, 0)
		cmds.add(cmd1)
		cmds.add(cmd2)
		

		cmds.upload()

	def connectDrone(self, UdpPort):
		print "Connected to vehicle: %s" % UdpPort
		vehicle= connect("127.0.0.1:%d" % UdpPort, wait_ready=True)
		
		return vehicle

	def doMission(self):
		self.lock.acquire()
		instanceDrone = drone.drone(self.vehicle)
		instanceDrone.startDrone()
		self.lock.release()
		vehicle = self.connectDrone(instanceDrone.UdpPort)

		vehicle.parameters['SYSID_THISMAV']= self.vehicle + 1
		
		self.uploadMission(vehicle)
		self.takeoff(vehicle, 10)

		print "Drone %s: Starting mission..." %self.vehicle

		vehicle.commands.next=0
	

		vehicle.mode = VehicleMode("AUTO")

		while True:
			time.sleep(2)
			nextwaypoint=vehicle.commands.next
			

			if (vehicle.location.global_relative_frame.alt <= 0):
            			print "Drone %s: Landing completed" %self.vehicle
            			break
		vehicle.close()

	def insertWaypoints(self, waypoint):
		self.waypoints.append(waypoint)
