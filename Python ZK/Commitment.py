from readline import read_init_file
from Crypto.Random import random
from Crypto.Hash import SHA256

# initialize P-256 prime
p = 2**256 - 2**224 + 2**192 + 2**96 - 1
security_parameter = 256
print("p:", p)

generate_new = False

m = 1
r = random.randint(1, p-1) if generate_new else 13135494537388068198112774104946649304594907867229462356834959420705414138495
#m = int.from_bytes(SHA256.new(message).digest(), byteorder='big')
#r = int.from_bytes(SHA256.new(blinding_factor).digest(), byteorder='big')
print('m:', m)
print('r:', r)

# TODO properly generate G and H
g = random.randint(1, p-1) if generate_new else 3007057779649931580237598654612510797095951971612630025891176454468165002055
h = random.randint(1, p-1) if generate_new else 20354936247998155748817459761265066334754915076915271771709029462851510023744

a = random.randint(1, p-1) if generate_new else 102226218488182575429617917198751009525280624180632774025827524848265712281483
s = random.randint(1, p-1) if generate_new else 25967183353325514799676581237678904227939120636021911759616725232453614868048
t = random.randint(1, p-1) if generate_new else 84686828729517342368149871861870093033884525046356658508611287770900160542511

print('g:', g)
print('h:', h)
print('a:', a)
print('s:', s)
print('t:', t)


C = pow(g, m, p) * pow(h, r, p) % p
Ca = pow(g, a, p) * pow(h, s, p) % p
Cb = pow(g, a*m, p) * pow(h, t, p) % p

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
right = pow(g, f, p) * pow(h, za, p) % p
check1 = left == right
check2 = pow(C, x-f, p) * Cb % p == pow(h, zb, p)
# sanity_check = (pow(g, (m*x +a) % p, p) * pow(h, (r*x + s) % p, p)) % p
# sanity_check2 = (pow(g, (m*x) % p, p) * pow(h, (r*x) % p, p) * pow(g, a, p) * pow(h, s, p)) % p
# sanity_check3 = (pow(pow(g, m, p) * pow(h, r, p) % p, x, p) * pow(g, a, p) * pow(h, s, p)) % p


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



print('check1:', check1)
print('check2:', check2)

# print('left:', left)
# print('right:', right)
# print('sanity_check:', sanity_check)
# print('sanity_check:', sanity_check)
# print('sanity_check2:', sanity_check2)
# print('sanity_check3:', sanity_check3)
# # print('why:', why)
# print ('{l} * {r} = {c}'.format(l=pow(g, (m*x) % p, p), r=pow(h, r*x, p), c=why))
# # print('tho:', tho)
# print('{l} * {r} = {c}'.format(l=pow(g, m, p), r=pow(h, r, p), c=tho))