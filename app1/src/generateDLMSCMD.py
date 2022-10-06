#!/usr/bin/python
import os
import re
import sys
import hashlib

""""
 In this case you need to produce n files from a template, liste of id and two dates.
dlms is a standard of communication in energy with iot object (smart meter)
You need to remplace the id of the template by the one in file  and change the sart and the stop date.



@filename_id : filename of the the list of  id 
@dt_start : a date in format YYYY-MM-DDTHH:MM:SS
@dt_stop : a date in format YYYY-MM-DDTHH:MM:SS
return the list of md5 for each xml string generated in list format ([...,...,...])

"""

def templating_dlms(filename_id,dt_start,dt_dtop):
	file = open(filename_id,"r")

	templateName = "data/media/tpl.xml" 

	tplFile = open(templateName,"r")
	tpl = tplFile.read()
	tplFile.close();

	dstart = "2019-08-16T13:35:00" if  (len(args)< 4) else args[3]
	dend = "2019-08-16T13:35:00" if  (len(args)< 5) else args[4]

	md5s=[]

	for line in file:
			print(line)
			newID = line.replace("\n","")
			prefix = "Activation_2.76"
			outName = "results/"+prefix+'_'+newID+".xml"
			
			str = re.sub("<devID>METER(.)+</devID>","<devID>"+newID+"</devID>",tpl,1)
			str = re.sub('taskId="'+prefix+'"','taskId="'+prefix+'_'+newID+'"',str,1)
			str = re.sub('<start>([^<])+</start>','<start>'+dstart+'</start>',str,1)
			str = re.sub('<stop>([^<])+</stop>','<stop>'+dend+'</stop>',str,1)
			md5s.append(hashlib.md5(str))
    return md5s


