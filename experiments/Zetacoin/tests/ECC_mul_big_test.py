from scripts import helpful_functions as hf
from scripts import crypto_helper as ch
from Crypto.Random import random
import math

def main():
    _max = 1154
    generate_new = False

    p = ch.p
    m = 1
    r = random.randint(2, _max) if generate_new else 1556
    print('m:', m)
    print('r:', r)


    C = ch.ECC_commit(m, r)

    # Generate x
    #x = random.getrandbits(128)
    xBig = ch.BigNum([0, 1])
    x = xBig.to_int()
    print('x:', x)

    # x*C

    xC = ch.ECC_mul(x, C)
    xC_big = ch.ECC_mul_big_test(xBig, C)

    print(f'xC: {xC.x}, {xC.y}')
    print(f'xC_big: {xC_big.x}, {xC_big.y}')
    print(f'xC_big == xC: {xC_big.x == xC.x and xC_big.y == xC.y}')

