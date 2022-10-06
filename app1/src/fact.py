import sys
""" 
#### factorial function example ### 
 fact n 
 n integer number
 commande_type fact
 args : n , positive integer 
 in  case of of negative return 0
"""

def factorielle(a):
    if a <2 :
        return 1
    else:
        return a*factorielle(a-1)

def cmd_fact(n):
    value=0
    value=str(factorielle(n))
    return value
