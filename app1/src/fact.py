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
    if a < 0:
        return 'undefined'
    if a < 2:
        return 1
    return a*factorielle(a-1)

def cmd_fact(n):
    return str(factorielle(n))
