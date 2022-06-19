
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Random import random
from brownie import convert
#import py_ecc.bn128 as bn
import math

def generate_g_and_h(verify, prime):
    g = 1
    while g == 1:
        r1 = random.randint(1, 2**256) if verify == False else 0xe4685df758000a656566de8bc8b7d87b0e9b0ae62f02919ea8ce24843c4bf36c
        f = int.from_bytes(SHA256.new(convert.to_bytes(r1)).digest(), byteorder='big')
        g = (f*f) % prime
    h = 1
    while h == 1 or h == g:
        r2 = random.randint(1, 2**256) if verify == False else 0xd4c74f4320562b43b69fcc771d85585275159e551743cb586b8aa4877736f99c
        f = int.from_bytes(SHA256.new(convert.to_bytes(r2)).digest(), byteorder='big')
        h = (f*f) % prime
    return g, h, r1, r2


#ffc_p = 2**256 - 2**224 + 2**192 + 2**96 - 1
#g = 3007057779649931580237598654612510797095951971612630025891176454468165002055
#h = 20354936247998155748817459761265066334754915076915271771709029462851510023744

ffc_p = 0x83b4f95d30d4f5c4d271f66f220b41547ad121eefbf8d2ab745e5cefd2ef3123
g = 0x57f7c5d58d84b91555c706fa707abfff239c1aa3229f7f59277e14f3925c5523
h = 0x378aa97c89749406b334da8fb9757af4e9d320820d474cf4cdad30d7f999f35f
#r1 = 0xe4685df758000a656566de8bc8b7d87b0e9b0ae62f02919ea8ce24843c4bf36c
#r2 = 0xd4c74f4320562b43b69fcc771d85585275159e551743cb586b8aa4877736f99c


# NIST P-256 elliptic curve parameters in hexadecimal form
# p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
# a = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
# b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b

# y^2 = x^3-3x+41058363725152142129326129780047268409114441015993725554835256314039467401291

# The P-256 prime
ecc_p = 2**256 - 2**224 + 2**192 + 2**96 - 1

G = ECC.construct(curve='P-256', point_x=0xc6147090dc789cd1827476f06c4080f727117427feb1ea10f5f58a1b8f26a646, point_y=0x9a8048d281edee5f5d7859ede6c7000ed420b55ac4604558c95b5e6f32de2276).pointQ
H = ECC.construct(curve='P-256', point_x=0x418ed4f85c649bf336d9e213337bfbb8d5e203c6ec1ad59d6c975e66b358bf3b, point_y=0xa479d9ab22e0c2e0fdf9659656b9efcd8f24da23cfc1eedfa852df9a1e621309).pointQ



def commit(m:int, r: int) -> int:
    return pow(g, m, ffc_p) * pow(h, r, ffc_p) % ffc_p

def ECC_commit(m:int, r: int) -> ECC.EccPoint:
    return ECC_mul(m, G) + ECC_mul(r, H)

# returns the scalar multiplication of a point P by a k
# if k is negative, point inversion is performed
def ECC_mul(k: int, point: ECC.EccPoint) -> ECC.EccPoint:
    if k < 0:
        return -k * -point
    else:
        return k * point

# Pad the list of commitments if its length is not a power of 2
def pad_commitments(C):
    n = len(C)
    N = 2**math.ceil(math.log(n, 2))
    if N == n:
        return C, n, N
    else:
        return C + [ECC_commit(42, 42)] * (N - n), n, N # this creates a new list

# calculates the number of bytes needed to represent the integer n
def bytes_needed(n: int) -> int:
    n = math.ceil(math.log(n, 2))
    n = math.ceil(n / 8)
    return n

class BigNum:
    # Constructor
    def __init__(self, val, neg = False):
        if isinstance(val, int):
            self.val = []
            bin_representation = bin(abs(val))[2:]
            # pad the binary representation with zeros to a multiple of 128 bits
            while len(bin_representation) % 128 != 0:
                bin_representation = '0' + bin_representation

            # append 128 bit chunks of x to arr
            for i in range(0, len(bin_representation), 128):
                self.val.append(int(bin_representation[i:i+128], 2))
            self.val.reverse()
            self.neg = val < 0
        else:
            self.val = val
            self.neg = neg 
    
    def to_int(self):
        num = 0
        for i in range(len(self.val)):
            num += self.val[i] * 2**(128*i)
        if self.neg:
            num = -num
        return num

    def to_tuple(self):
        return (tuple(self.val), self.neg)

    def __add__(self, other):
        return BigNum(self.to_int() + other.to_int())

    def __sub__(self, other):
        return BigNum(self.to_int() - other.to_int())
    
    def __mul__(self, other):
        return BigNum(self.to_int() * other.to_int())

    def __eq__(self, other):
        return self.to_int() == other.to_int()

    def __str__(self):
        return str(self.to_int())


# Convert an int to a big_num


#TODO: Write unit tetsts for calc_coeffs
# Calculate the coefficients p_{i,k} for the product of f_{j, i_j} for j from 0 to n-1
def calc_coeffs(n, i, l, A):
    coeffs = [0] * n
    coeffs[0] = 1
    for j in range(n):
        # i_j == 1 && l_j == 1 => x + a_j
        # i_j == 1 && l_j == 0 => a_j
        # i_j == 0 && l_j == 1 => -a_j
        # i_j == 0 && l_j == 0 => x - a_j
        if i >> j & 1 == 1:
            if l >> j & 1 == 1:
                # x + aj
                new_coeffs = []
                for k in range(n):
                    new_coeffs.append(coeffs[k] * A[j])
                    if k != 0:
                        new_coeffs[k] = coeffs[k-1] + new_coeffs[k]
                coeffs = new_coeffs
            else:
                # aj
                for k in range(n):
                    coeffs[k] *= A[j]
        else:
            if l >> j & 1 == 1:
                # -aj
                for k in range(n):
                    coeffs[k] *= -A[j]
            else:
                # x - aj
                new_coeffs = []
                for k in range(n):
                    new_coeffs.append(coeffs[k] * -A[j])
                    if k != 0:
                        new_coeffs[k] = coeffs[k-1] + new_coeffs[k]
                coeffs = new_coeffs
    return coeffs


def ECC_mul_big_test(scalar: BigNum, point: ECC.EccPoint):
    x = point.point_at_infinity()
    # print(f'Point at infinity: {x.x, x.y}')
    if scalar.neg == True:
        for i in range(len(scalar.val)):
            xInv = -point
            for _ in range(i):
                xInv = 2**128 * xInv
            xInv = scalar.val[i] * xInv
            x = x + xInv
            # print('negative')
            # print('x:', x.x, x.y)
            # print(f'scalar.val[{i}]:', scalar.val[i])
    elif scalar.to_int() != 0:
        for i in range(len(scalar.val)):
            tmp = point
            for _ in range(i):
                tmp = 2**128 * tmp
            tmp = tmp * scalar.val[i]
            x = x + tmp
            # print('positive and not 0')
            # print('x:', x.x, x.y)
    return x
