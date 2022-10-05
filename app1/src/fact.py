import sys
## fact example 
## fact n 
## n integer number
## commande_type fact
## args : 10  

def factorielle(a):
    if a <2 :
        return 1
    else:
        return a*factorielle(a-1)

if len(sys.argv)>1 :
    if type(3) == type(int(sys.argv[1])) :
        print(str(factorielle(int(sys.argv[1]))))
    else:
        print("usage fact $number")
else:
    print("usage fact $number")
