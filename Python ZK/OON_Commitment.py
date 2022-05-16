from Crypto.Random import random
from CryptoHelper import *
import math

security_parameter = 256
print("p:", p)

generate_new = True

# Create a list of commitments, one of which is a commitment to 0
commitments = []
l = 0
n = 3
N = 2**n
assert l < N, "l must be less than N"
assert N == 2**math.ceil(math.log(N, 2)), "N must be a power of 2"

for i in range(N):
    m = random.randint(1, p-1) if generate_new else i
    r = random.randint(1, p-1) if generate_new else i
    commitments.append(Commit(m, r))
commitments[l] = Commit(0, random.randint(1, p-1) if generate_new else 223)


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


    Cl.append(Commit(l >> j & 1, r)) # Commit to the jth bit of l
    Ca.append(Commit(a, s))
    Cb.append(Commit(a*(l >> j & 1), t))


# The coefficients depend on the values of A
coeffs = [calc_coeffs(n, i, l, A) for i in range(N)]

for j in range(n):
    # Calculate Cd value
    product = 1
    for i in range(n):
        product *= pow(commitments[i], coeffs[i][j], p) * Commit(0, P[j])
    Cd.append(product)


# Generate x
x = random.getrandbits(security_parameter) if generate_new else 310010182257446143905433863762199680188
print('x:', x)


F = []
Za = []
Zb = []
for j in range(n):
    f = (l << j & 1) * x + A[j]
    za = R[j] * x + S[j]
    zb = R[j] * (x-f) + T[j]
    F.append(f)
    Za.append(za)
    Zb.append(zb)

r = R[0]
zd = r * pow(x, n, p) - sum([P[k] * pow(x, k, p) for k in range(n)])

#Vefify the proof
print('Verifying...')

for j in range(n):
    left = pow(Cl[j], x, p) * Ca[j] % p
    right = Commit(F[j], Za[j])
    print('Check 0.{j}: {true}'.format(j=j, true=left == right))

for j in range(n):
    left = pow(Cl[j], x-F[j], p) * Cb[j] % p
    right = Commit(0, Zb[j])
    print('Check 1.{j}: {true}'.format(j=j, true=left == right))