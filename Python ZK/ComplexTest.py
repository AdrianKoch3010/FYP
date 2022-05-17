from Crypto.Random import random
from CryptoHelper import *
import math

security_parameter = 256
# print("p:", p)
# print('security_parameter:', security_parameter)

generate_new = False

# Create a list of commitments, one of which is a commitment to 0
commitments = []
l = 0
n = 1
N = 2
r_0_commitment = random.randint(1, p-1) if generate_new else 9
commitments.append(Commit(0, r_0_commitment))
commitments.append(Commit(2, random.randint(1, p-1) if generate_new else 15))
print('commitments:', commitments)
A = []
P = []
Cd = []

for j in range(n):
    a = random.randint(1, p-1) if generate_new else (j + 1) * 3
    _p = random.randint(1, p-1) if generate_new else (j + 1) * 3
    A.append(a)
    P.append(_p)
print('A:', A)
print('P:', P)

# The coefficients depend on the values of A
coeffs = [calc_coeffs(n, i, l, A) for i in range(N)]
print('coeffs:', coeffs)

for j in range(n):
    # Calculate Cd value
    product = 1
    for i in range(N):
        product *= pow(commitments[i], coeffs[i][j], p) % p
    cd = product * Commit(0, P[j]) % p
    Cd.append(cd)
print('Cd:', Cd)


# Generate x
x = random.getrandbits(security_parameter) if generate_new else 21
print('x:', x)


F = []
for j in range(n):
    l_j = l >> j & 1
    f = l_j * x + A[j]
    F.append(f)

print('F:', F)

#r = R[l] # the r used for the commitment to 0
zd = r_0_commitment * pow(x, n) - sum([P[k] * pow(x, k) for k in range(n)])
print('zd:', zd)

#Vefify the proof
print('Verifying...')

print('Checking commitment to 0')
outer_product = 1
for i in range(N):
    # Calculate the product of f_j,i_j
    product = 1
    for j in range(n):
        i_j = i >> j & 1
        if i_j == 1:
            product *= F[j]
        else:
            product *= x - F[j]
    print('inner product:', product)
    outer_product *= pow(commitments[i], product, p) % p
left_product = outer_product

# Calculate the product of the other commitments
product = 1
for k in range(n):
    product *= pow(Cd[k], -pow(x, k), p) % p
right_product = product
print('right product:', right_product)

left = left_product * right_product % p
right = Commit(0, zd)
print('left:', left)
print('right:', right)
print('Check 2: {true}'.format(true=left == right))