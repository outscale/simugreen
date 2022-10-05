import io
import sys

#computing a list of max from a key/value input
# input :
#     * a filename to a file with the list of couple of letter(key) and an integer (value) as (a,3) separate by ';' # output 
#     * x number of max to return
# ouput :
#     the list key of the keys of the n max value as python list [a,f,3]
# the resolution must be done in less time than the naive implemented here on big files tests
#____________
# command : max pathfile x
# x must be changed to 1 of negative or null  
# the naive algorithm implemeted 
# run is the function called by the test runner

path_to_list_key_value=argv[1]
nbmax=int(argv[2])
if nbmax<1: 
    nbmax=1  

def max_in_list(s): 
    pairs=s.replace("(",'').replace(")","").split(';')
    m = -1
    key= "NONE"
    d={}
    for pair in pairs:
        kv=pair.split(',')
        i=int(kv[1])
        d[kv[0]]=i
        if(m < i):
            m=i
            key=kv[0]
    
    return key+","+m

flist=open(argv[1],'r')
s=flist.read()
keys=[]
while keys.len < nbmax :
    max=max_in_list(s)
    keys.append(max.split(",")[0])
    s=s.replace("("+max+");").replace(";("+max+")")

print(keys)








