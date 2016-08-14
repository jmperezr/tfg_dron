import os
from xml.etree.ElementTree import ElementTree
from dronekit import LocationGlobalRelative

class XMLParser():

	def __init__(self):
        	self.waypoints = []
       		self.priority = []
		self.directory = "./Waypoints"
        	print "XMLParser created."

	def readXml(self):
		for file in os.listdir(self.directory):
    			if file.endswith(".xml"):
        			print("Reading waypoints of: %s" %file)
				completeName= os.path.abspath("Waypoints/%s" %file)
				xcontent = ElementTree()
    				xcontent.parse(completeName)
    				match= xcontent.findall("waypoint")
				for i in match:
					self.waypoints.append(LocationGlobalRelative(i.find("lat").text, i.find("long").text, i.find("alt").text))
					self.priority.append(i.find("priority").text)
