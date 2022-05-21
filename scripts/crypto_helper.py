
from Crypto.PublicKey import ECC
import math

# NIST P-256 elliptic curve parameters in hexadecimal form
# p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
# a = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
# b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b


# y^2 = x^3-3x+41058363725152142129326129780047268409114441015993725554835256314039467401291

# The P-256 prime
p = 2**256 - 2**224 + 2**192 + 2**96 - 1

# The secp256k1 prime
#p = 2**256 - 2**32 - 977

# g = 3007057779649931580237598654612510797095951971612630025891176454468165002055
# h = 20354936247998155748817459761265066334754915076915271771709029462851510023744


G = ECC.construct(curve='P-256', point_x=0xc6147090dc789cd1827476f06c4080f727117427feb1ea10f5f58a1b8f26a646, point_y=0x9a8048d281edee5f5d7859ede6c7000ed420b55ac4604558c95b5e6f32de2276).pointQ
H = ECC.construct(curve='P-256', point_x=0x418ed4f85c649bf336d9e213337bfbb8d5e203c6ec1ad59d6c975e66b358bf3b, point_y=0xa479d9ab22e0c2e0fdf9659656b9efcd8f24da23cfc1eedfa852df9a1e621309).pointQ

# def commit(m:int, r: int) -> int:
#     return pow(g, m, p) * pow(h, r, p) % p

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
def pad_commitments(C: list) -> (list, int, int):
    n = len(C)
    N = 2**math.ceil(math.log(n, 2))
    if N == n:
        return C, n, N
    else:
        return C + [ECC_commit(0, 0)] * (N - n), n, N # this creates a new list

# calculates the number of bytes needed to represent the integer n
def bytes_needed(n: int) -> int:
    n = math.ceil(math.log(n, 2))
    n = math.ceil(n / 8)


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

# print([calc_coeffs(3, i, 0b101, [3, 2, 5]) for i in range(8)])