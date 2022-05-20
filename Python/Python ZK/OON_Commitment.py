from Crypto.Random import random
from CryptoHelper import *
import math

#TODO: check if the random number is in the right range
# It might have to be in the range [2, p-2]

security_parameter = 256
print("p:", p)
print('security_parameter:', security_parameter)

generate_new = True

# Create a list of commitments, one of which is a commitment to 0
commitments = []
l = 7
n = 3
N = 2**n
r_0_commitment = 0
assert l < N, "l must be less than N"
assert N == 2**math.ceil(math.log(N, 2)), "N must be a power of 2"

for i in range(N):
    if i == l:
        m = 0
    else:
        m = random.randint(1, p-1) if generate_new else (i + 234) * 5672
    r = random.randint(1, p-1) if generate_new else (i + 9876) * 987654321
    r_0_commitment = r if i == l else r_0_commitment
    commitments.append(commit(m, r))


R = []
A = []
S = []
T = []
P = []
Cl = []
Ca = []
Cb = []
Cd = []

for j in range(n):
    r = random.randint(1, p-1) if generate_new else (j + 87654) * 34567
    a = random.randint(1, p-1) if generate_new else (j + 4344) * 3543
    s = random.randint(1, p-1) if generate_new else (j + 234) * 354
    t = random.randint(1, p-1) if generate_new else (j + 4345) * 3456
    _p = random.randint(1, p-1) if generate_new else (j + 534) * 97373
    R.append(r)
    A.append(a)
    S.append(s)
    T.append(t)
    P.append(_p)

    l_j = l >> j & 1
    print('l_{j}:'.format(j = j), l_j)
    Cl.append(commit(l_j, r)) # commit to the jth bit of l
    Ca.append(commit(a, s))
    Cb.append(commit(l_j*a, t))


# The coefficients depend on the values of A
coeffs = [calc_coeffs(n, i, l, A) for i in range(N)]

for j in range(n):
    # Calculate Cd value
    product = 1
    for i in range(N):
        product *= pow(commitments[i], coeffs[i][j], p) % p
    cd = product * commit(0, P[j]) % p
    Cd.append(cd)


# Generate x
x = random.getrandbits(security_parameter) if generate_new else 310010182257446143905433863762199680188
print('x:', x)


F = []
Za = []
Zb = []
for j in range(n):
    l_j = l >> j & 1
    f = l_j * x + A[j]
    za = R[j] * x + S[j]
    zb = R[j] * (x-f) + T[j]
    F.append(f)
    Za.append(za)
    Zb.append(zb)

#r = R[l] # the r used for the commitment to 0
zd = r_0_commitment * pow(x, n) - sum([P[k] * pow(x, k) for k in range(n)])

#Vefify the proof
print('Verifying...')

print('Checking commitments to l')
for j in range(n):
    left = pow(Cl[j], x, p) * Ca[j] % p
    right = commit(F[j], Za[j])
    print('Check 0.{j}: {true}'.format(j=j, true=left == right))

for j in range(n):
    left = pow(Cl[j], x-F[j], p) * Cb[j] % p
    right = commit(0, Zb[j])
    print('Check 1.{j}: {true}'.format(j=j, true=left == right))

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
    outer_product *= pow(commitments[i], product, p) % p
left_product = outer_product

# Calculate the product of the other commitments
product = 1
for k in range(n):
    product *= pow(Cd[k], -pow(x, k), p) % p
right_product = product

left = left_product * right_product % p
right = commit(0, zd)
print('Check 2: {true}'.format(true=left == right))