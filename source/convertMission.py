import sys
import os
from xml.etree.ElementTree import ElementTree

def Readthexml(f):
    """Read the file from the argument list and dump the title contents and keywords"""
    xcontent = ElementTree()
    xcontent.parse(f)
    index = 0
    match= xcontent.findall("waypoint")
    doc = ["QGC WPL 110\n"]			#Head
    for i in match:
    	doc.append(str(index)) 			#Index
	if(index == 0):	
		doc.append("\t1") 		#Mission Start
		doc.append("\t0")		#Cord Frame
	else:	
		doc.append("\t0") 		#Mission Start
		doc.append("\t3")		#Cord Frame
	
	doc.append("\t16")			#Command
	doc.append("\t0")			#Param1
	doc.append("\t5")			#Param2
	doc.append("\t0")			#Param3
	doc.append("\t0")			#Param4
	doc.append("\t"+i.find("long").text)	#Param5
	doc.append("\t"+i.find("lat").text)	#Param6
	doc.append("\t"+i.find("alt").text)	#Param7
	doc.append("\t1\n")			#Autocontinue
	index += 1
	

    completeName = os.path.abspath("./Missions/%s_%s.txt") % (xcontent.find("priority").text, f)
    out = open(completeName,"w")
    out.write("".join(doc))
    return True

def main(argv=None):
    if argv is None:
        argv = sys.argv
        args = argv[1:]
        for arg in args:
            if os.path.exists(arg):
                Readthexml(arg)
	    else:
		print "Error: file does not exist"

if __name__ == "__main__":
    main()
