from Crypto.Random import random
from CryptoHelper import *

# initialize P-256 prime
#p = 2**256 - 2**224 + 2**192 + 2**96 - 1
security_parameter = 256
print("p:", p)

generate_new = False

m = 1
r = random.randint(1, p-1) if generate_new else 13135494537388068198112774104946649304594907867229462356834959420705414138495

print('m:', m)
print('r:', r)

a = random.randint(1, p-1) if generate_new else 102226218488182575429617917198751009525280624180632774025827524848265712281483
s = random.randint(1, p-1) if generate_new else 25967183353325514799676581237678904227939120636021911759616725232453614868048
t = random.randint(1, p-1) if generate_new else 84686828729517342368149871861870093033884525046356658508611287770900160542511

print('g:', g)
print('h:', h)
print('a:', a)
print('s:', s)
print('t:', t)


C = commit(m, r)
Ca = commit(a, s)
Cb = commit(a*m, t)

# Generate x
x = random.getrandbits(security_parameter) if generate_new else 310010182257446143905433863762199680188
print('x:', x)

f = m*x + a
za = r*x + s
zb = r * (x-f) + t
print('f:', f)
print('za:', za)
print('zb:', zb)

# Verify the proof
left = pow(C, x, p) * Ca % p
right = commit(f, za)
check1 = left == right
check2 = pow(C, x-f, p) * Cb % p == commit(0, zb)

print('check1:', check1)
print('check2:', check2)
# p = 37
# m = 1
# r = 20
# g = 5
# h = 7
# x = 22
# a = 11
# s = 13
# t = 17
# f = m*x + a
# za = r*x + s
# zb = (r*(x-f) + t)
# C = (pow(g, m, p) * pow(h, r, p)) % p
# Cb = (pow(g, a*m, p) * pow(h, t, p)) % p

# left = (pow(C, x-f, p) * Cb) % p
# right = (pow(h, zb, p))
# sanity_check = (pow(g, m*x - m*m*x) * pow(h, r * (x-f) + t, p)) % p
