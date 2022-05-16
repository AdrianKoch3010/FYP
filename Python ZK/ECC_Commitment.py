from Crypto.PublicKey import ECC
from Crypto.Random import random
from Crypto.Hash import SHA256


# initialize P-256 prime
p = 2**256 - 2**224 + 2**192 + 2**96 - 1
print("p:", p)


m = 0
r = random.randint(1, p-1)
#m = int.from_bytes(SHA256.new(message).digest(), byteorder='big')
#r = int.from_bytes(SHA256.new(blinding_factor).digest(), byteorder='big')
print('m:', m)
print('r:', r)

G = ECC.generate(curve='P-256').pointQ
H = ECC.generate(curve='P-256').pointQ

a = random.randint(1, p-1)
s = random.randint(1, p-1)
t = random.randint(1, p-1)


C = m * G + r * H
Ca = a * G + s * H
Cb = (a*m) * G + t * H
#print('c: {c.x}, {c.y}'.format(c=c))

# Generate x
x = random.getrandbits(128)
print('x:', x)

f = m*x + a
za = r*x + s
zb = r*(x-f) + t
print('f:', f)
print('za:', za)
print('zb:', zb)

# Verify the proof
check1 = x * C + Ca == f * G + za * H
check2 = ((x-f) % p) * C + Cb == (zb % p) * H

print('check1:', check1)
print('check2:', check2)