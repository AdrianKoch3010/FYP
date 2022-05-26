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


def main():
    # Deploy the contract
    proof_verifier = deploy()

    # create one big number as bytes´
    a = 2
    b = 2

    # calculate number of bits of a
    # a_bits = int(math.log(a, 2)) + 1
    a_data = [[a, b], False]

    # calculate number of bits of b
    # b_bits = int(math.log(b, 2)) + 1
    b_data = [[b], False]

    # print('a_data:', a_data)
    # print('b_data:', b_data)

    result = proof_verifier.addBig(a_data, b_data)
    print('result: ', result)