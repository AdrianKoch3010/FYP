from Python.Python_Zerocoin.HelperFunctions import G
from brownie import ProofVerifier, ECC, EllipticCurve, BigNum, accounts, network, config
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
    ECC.deploy({'from': account}, publish_source=pub_source)
    BigNum.deploy({'from': account}, publish_source=pub_source)
    # deploy the proof verifier
    proof_verifier = ProofVerifier.deploy({'from': account}, publish_source=pub_source)
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