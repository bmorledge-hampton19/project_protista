# First, get all prime numbers greater than or equal to 251 but less than or equal to 100000/251 using the sieve method

def sieveOfEratosthenes(n): 

    potentialPrimes = [True for i in range(n+1)] 
    primes = list()
      
    p = 2
    while(p * p <= n): 
           
        # If this potential prime is not changed, then it is a prime 
        if (potentialPrimes[p] == True): 
               
            # Update all multiples of p 
            for i in range(p * p, n + 1, p): 
                potentialPrimes[i] = False

            primes.append(p)
        p += 1

    return primes

# Get the prime values that could potentially produce problematic products.
primes = sieveOfEratosthenes(int(999999/251)**2)
primes = [prime for prime in primes if prime >= 251]
print("Possible prime factors:",primes)
print()

# Compute the problematic products.
validPrimeProducts = set()

for i in range(0, len(primes)):
    for j in range(i, len(primes)):
        if primes[i]*primes[j] <= 999999: validPrimeProducts.add(primes[i]*primes[j])

print("Possible prime products:",validPrimeProducts)
print()

# What is the probability that rebeca chose such a hard number by chance?
probabilityRebecaChoosesEasier = 1
for validPrimeProduct in validPrimeProducts:
    probabilityRebecaChoosesEasier *= (1-1/validPrimeProduct)
probabilityRebecaChoosesAsHardOrHarder = 1- probabilityRebecaChoosesEasier

print("Probability Rebeca chooses as hard or harder by random chance:",probabilityRebecaChoosesAsHardOrHarder)