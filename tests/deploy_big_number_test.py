from Python.Python_Zerocoin.HelperFunctions import G
from brownie import ProofVerifierTest, ECC, EllipticCurve, BigNum, accounts, network, config
from web3 import Web3
from scripts import helpful_functions as hf
from scripts import crypto_helper as ch
from Crypto.Random import random
import math

def deploy():
    account = hf.get_account()

    pub_source = publish_source=config['networks'][network.show_active()]['verify']
    # deploy the libraries
    EllipticCurve.deploy({'from': account}, publish_source=pub_source)
    BigNum.deploy({'from': account}, publish_source=pub_source)
    ECC.deploy({'from': account}, publish_source=pub_source)
    # deploy the proof verifier
    proof_verifier = ProofVerifierTest.deploy({'from': account}, publish_source=pub_source)
    print(f"Deployed ProofVerifier to address: {proof_verifier.address}")
    return proof_verifier

# def convert_to_bn(x):
#     arr = []
#     bin_representation = bin(x)[2:]
#     # pad the binary representation with zeros to a multiple of 128 bits
#     while len(bin_representation) % 128 != 0:
#         bin_representation = '0' + bin_representation

#     # append 128 bit chunks of x to arr
#     for i in range(0, len(bin_representation), 128):
#         arr.append(int(bin_representation[i:i+128], 2))
#     arr.reverse()
#     return arr

# def convert_bn_to_int(arr):
#     x = 0
#     for i in range(len(arr)):
#         x += arr[i] * 2**(128*i)
#     return x

def main():
    # Deploy the contract
    proof_verifier = deploy()

    # create one big number as bytes´
    num = 2**128 - 1

    a = ch.BigNum([num, num], False)
    b = ch.BigNum([0, num], True)

    print('a:', a.to_int())
    print('b:', b.to_int())

    # Testing addBig
    print('\n\nTesting addBig...')
    tx_result = proof_verifier.addBig(a.to_tuple(), b.to_tuple())
    result = ch.BigNum(tx_result[0], tx_result[1])
    print('result:', result)
    print('a + b == result:', a + b == result)

    # Testing subBig
    print('\n\nTesting subBig...')
    tx_result = proof_verifier.subBig(a.to_tuple(), b.to_tuple())
    result = ch.BigNum(tx_result[0], tx_result[1])
    print('result:', result)
    print('a-b == result:', a - b)
    print('a-b == result:', a - b == result)

    # Testing mulBig
    print('\n\nTesting mulBig...')
    tx_result = proof_verifier.mulBig(a.to_tuple(), b.to_tuple())
    result = ch.BigNum(tx_result[0], tx_result[1])
    print('result:', result)
    print('a*b == result:', a * b == result)

    # Testing ecc mul
    print('\n\nTesting ecc mul...')
    m = 1
    r = 1556
    #print('m:', m)
    #print('r:', r)

    C = ch.ECC_commit(m, r)
    x = 51651565615123116851231681351681321681318613516813163841351385541023186512035132135567116845334513248613216843168153
    x_big = ch.BigNum(x)
    print('x:', x)
    print('big_x:', x_big.val)

    # x*C
    xC = ch.ECC_mul(x, C)
    #xC_big = ch.ECC_mul_big_test(xBig, C)

    print(f'xC: {xC.x}, {xC.y}')

    result = proof_verifier.testEccMul(x_big.to_tuple(), [C.x, C.y])
    print(f'result: {result[0]}, {result[1]}')
    print(f'xC == result: {xC.x == result[0] and xC.y == result[1]}')

    #print(f'xC_big: {xC_big.x}, {xC_big.y}')
    #print(f'xC_big == xC: {xC_big.x == xC.x and xC_big.y == xC.y}')