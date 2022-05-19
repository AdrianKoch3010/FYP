
from Crypto.PublicKey import ECC

p = 2**256 - 2**224 + 2**192 + 2**96 - 1
g = 3007057779649931580237598654612510797095951971612630025891176454468165002055
h = 20354936247998155748817459761265066334754915076915271771709029462851510023744

G = ECC.generate(curve='P-256').pointQ
H = ECC.generate(curve='P-256').pointQ

def commit(m:int, r: int) -> int:
    return pow(g, m, p) * pow(h, r, p) % p

def ECC_commit(m:int, r: int) -> ECC.EccPoint:
    return ECC_mul(m, G) + ECC_mul(r, H)

def ECC_mul(k: int, point: ECC.EccPoint) -> ECC.EccPoint:
    if k < 0:
        return -k * -point
    else:
        return k * point

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