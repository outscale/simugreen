def is_prime(n):
    if n < 2:
        return False
    for i in range(2,n):
        if (n%i) == 0:
            return False
    return True

def prime_list(n):
    """Return a list of all the prime numbers inferior or equal to n"""
    result = []
    for i in range(n+1):
        if is_prime(i):
            result.append(i)
    return result