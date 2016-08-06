import os
import sys
import time
import dronekit_sitl
from dronekit import connect, Command, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import drone
import FPVSystem
import thread
from threading import Thread
import threading
import socket
import exceptions
import dronekit

class proxyDrone():
	def __init__(self, numVehicle, lock):
        	self.waypoint = None
        	self.status = "idle"
		self.numVehicle = numVehicle
		self.lock = lock
		self.vehicle = None
		self.inFlight = False
		self.numWaypoints = 0
		self.FPV = None
        	print "Proxy created."

	def takeoff(self, aTargetAltitude):

    		print "Drone %s: Basic pre-arm checks" %self.numVehicle
    		
    		while not self.vehicle.is_armable:
        		print "  Drone %s: Waiting for vehicle to initialise..." %self.numVehicle
        		time.sleep(2)

        
    		print "Drone %s: Arming motors" %self.numVehicle
    		# vehicle Copter must be armed in guided mode
    		self.vehicle.mode = VehicleMode("GUIDED")
    		self.vehicle.armed = True    

    		while not self.vehicle.armed:      
        		print "  Drone %s: Waiting for arming..." %self.numVehicle
        		time.sleep(2)

    		print "Drone %s: Takeoff!!" %self.numVehicle
    		self.vehicle.simple_takeoff(aTargetAltitude) 

       		while True:
        		print "Drone %s: Altitude: %s" %(self.numVehicle, self.vehicle.location.global_relative_frame.alt)      
        		if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude*0.95:
            			print "Drone %s: Reached target altitude" %self.numVehicle
            			break
        		time.sleep(2)

	def uploadMission(self, land, secondWait):
		cmds = self.vehicle.commands
				
		cmds.clear()
	
		cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10))
		cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, float(self.waypoint.lon) , float(self.waypoint.lat), float(self.waypoint.alt)))
		cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LOITER_TIME, 0, 0, secondWait, 0, 0, 0, 0 , 0, 0))
		cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, float(self.waypoint.lon) , float(self.waypoint.lat), float(self.waypoint.alt)))
		cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0))
		cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0,  0, 0, 0))
		cmds.upload()
		
	def connectDrone(self, secondsPerPhoto):
		self.lock.acquire()
		instanceDrone = drone.drone(self.numVehicle)
		instanceDrone.startDrone()
		print "Connected to vehicle: %s" % instanceDrone.UdpPort
		try:
			self.vehicle = connect('127.0.0.1:%s' % instanceDrone.UdpPort, wait_ready = True)
			#	self.vehicle = connect('/dev/ttyUSB0', wait_ready = True)
			self.vehicle.parameters['SYSID_THISMAV'] = self.numVehicle + 1
		# Bad TCP connection
		except socket.error:
    			print 'No server exists!'

		# Bad TTY connection
		except exceptions.OSError as e:
    			print 'No serial exists!'

		# API Error
		except dronekit.APIException:
    			print 'Timeout!'
		
		# Other error
		except:
    			print 'Some other error!'

		self.lock.release()
		
		self.FPV = FPVSystem.FPVSystem(secondsPerPhoto, self.numVehicle)
		t = threading.Thread(target=self.FPV.videoCapture)
		t.daemon = True
		t.start()

		self.takeoff(10)
		self.inFlight = True
			
	def doMission(self, land, secondWait):
		
		if not land:
			self.uploadMission(land, secondWait)

		print "Drone %s: Starting mission..." %self.numVehicle

		self.vehicle.commands.next = 0

		self.vehicle.mode = VehicleMode("AUTO")

		while True:
			time.sleep(2)
			nextwaypoint = self.vehicle.commands.next

			if not land and self.numWaypoints == 1:
				if nextwaypoint >=3 : #Dummy waypoint
        				print "Drone %s: Next waypoint..." %self.numVehicle
        				break;
			elif not land and self.numWaypoints > 1:
				if nextwaypoint >=4 : #Dummy waypoint
        				print "Drone %s: Next waypoint..." %self.numVehicle
        				break;
			else:
				if self.vehicle.location.global_relative_frame.alt <= 0:
            				print "Drone %s: Landing completed" %self.numVehicle
					print "Drone %s: %s waypoints visited" %(self.numVehicle, self.numWaypoints)
					self.vehicle.close()
					self.FPV.stopVideoCapture = True
					break
		#self.vehicle.close()
		self.status = "idle"
	
	def insertWaypoints(self, waypoint):
		self.status = "busy"
		self.waypoint = waypoint
		self.numWaypoints = self.numWaypoints + 1
		
