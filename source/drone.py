import os
import subprocess

class drone():
	def __init__(self, numVehicle):
        	self.numVehicle = numVehicle
		self.UdpPort = 14550 + numVehicle
		self.instance = 1 + numVehicle
		self.currentDir = os.getcwd()
        	print "Drone %s launched." %numVehicle
	
	def startDrone(self):
		if self.numVehicle == 0:
			os.chdir(os.path.expanduser("~/ardupilot/ArduCopter/"))
		
		elif self.numVehicle == 1:
			os.chdir(os.path.expanduser("~/ardupilot2/ArduCopter/"))
		else:					
			os.chdir(os.path.expanduser("~/ardupilot3/ArduCopter/"))

		#cmd= 'gnome-terminal -x bash -c "sim_vehicle.sh -I %d -L prueba --console --map --out 127.0.0.1:%d --aircraft test && bash"' % (self.instance, self.UdpPort)
		cmd= 'gnome-terminal -x bash -c "sim_vehicle.sh -I %d -L prueba --map --out 127.0.0.1:%d --aircraft test && bash"' % (self.instance, self.UdpPort)
		subprocess.call(cmd, shell=True)
		os.chdir(self.currentDir)
