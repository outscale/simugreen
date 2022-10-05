#!/usr/bin/python
import os
import re
import sys
###
# This scripts using two files to produces n command dlms files  based on
#  - list of meter( an iot object)
#  - list of IDS of this meter
#  elements changed in the template are the id,date start and date stop
#
#



args = sys.argv
print(args)
if ( (len(args)>1) and args[1]== "-h"):
	sys.exit("usage : python "+args[0]+" [filename_id] [filename_template] [date_start] [date_stop]")


filename = "id.txt" if  (len(args)< 2) else args[1]

file = open(filename,"r")

templateName = "tpl.xml" if  (len(args)< 3) else args[2]

tplFile = open(templateName,"r")
tpl = tplFile.read()
tplFile.close();

dstart = "2019-08-16T13:35:00" if  (len(args)< 4) else args[3]
dend = "2019-08-16T13:35:00" if  (len(args)< 5) else args[4]


try:
	for  (dirpath, dirnames, files)  in os.walk("results"):   
		if  files != []:
			for f in files : os.remove("results/"+f)
		os.rmdir("results")
	os.mkdir("results")
except OSError as e:
	print("creation directory failed\n"+e)
else:
	for line in file:
		print(line)
		newID = line.replace("\n","")
		prefix = "Activation_2.76"
		outName = "results/"+prefix+'_'+newID+".xml"
		out = open(outName,"w")
		str = re.sub("<devID>METER(.)+</devID>","<devID>"+newID+"</devID>",tpl,1)
		str = re.sub('taskId="'+prefix+'"','taskId="'+prefix+'_'+newID+'"',str,1)
		str = re.sub('<start>([^<])+</start>','<start>'+dstart+'</start>',str,1)
		str = re.sub('<stop>([^<])+</stop>','<stop>'+dend+'</stop>',str,1)
		print(str)
		out.writelines(str)
		out.close()

file.close();
