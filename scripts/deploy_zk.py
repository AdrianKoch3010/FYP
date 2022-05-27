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
    BigNum.deploy({'from': account}, publish_source=pub_source)
    ECC.deploy({'from': account}, publish_source=pub_source)
    # deploy the proof verifier
    proof_verifier = ProofVerifier.deploy({'from': account}, publish_source=pub_source)
    print(f"Deployed ProofVerifier to address: {proof_verifier.address}")
    return proof_verifier


def main():
    # Deploy the contract
    proof_verifier = deploy()

    # Attempt to verify a proof
    # proof structure:
    # ECC.Point c_a;
    # ECC.Point c_b;
    # uint256 f;
    # uint256 z_a;
    # uint256 z_b;
    
    _max = 1154
    generate_new = False

    p = ch.p
    m = 1
    r = random.randint(2, _max) if generate_new else 1556
    #m = int.from_bytes(SHA256.new(message).digest(), byteorder='big')
    #r = int.from_bytes(SHA256.new(blinding_factor).digest(), byteorder='big')
    print('m:', m)
    print('r:', r)

    #G = ECC.generate(curve='P-256').pointQ
    #H = ECC.generate(curve='P-256').pointQ

    a = random.randint(2, _max) if generate_new else 455
    s = random.randint(2, _max) if generate_new else 567
    t = random.randint(2, _max) if generate_new else 678


    # C = m * G + r * H
    # Ca = a * G + s * H
    # Cb = (a*m) * G + t * H
    #print('c: {c.x}, {c.y}'.format(c=c))
    C = ch.ECC_commit(m, r)
    Ca = ch.ECC_commit(a, s)
    Cb = ch.ECC_commit(a*m, t)

    # Generate x
    #x = random.getrandbits(128)
    x = ch.BigNum([1, 1]).to_int()
    print('x:', x)

    f = m*x + a
    za = r*x + s
    zb = r*(x-f) + t

    #print the amount of bits of C.x
    # print('C.x: ', C.x)
    # print('C.y: ', C.y)
    # print('Ca.x: ', Ca.x)
    # print('Ca.y: ', Ca.y)
    # print('Cb.x: ', Cb.x)
    # print('Cb.y: ', Cb.y)
    # print('f:', f)
    # print('za:', za)
    # print('zb:', zb)

    print('p:', math.ceil(math.log(p, 2)))
    print('C.x: ', math.ceil(math.log(C.x, 2)))
    print('C.y: ', math.ceil(math.log(C.y, 2)))
    print('Ca.x: ', math.ceil(math.log(Ca.x, 2)))
    print('Ca.y: ', math.ceil(math.log(Ca.y, 2)))
    print('Cb.x: ', math.ceil(math.log(Cb.x, 2)))
    print('Cb.y: ', math.ceil(math.log(Cb.y, 2)))
    print('f: ', math.ceil(math.log(f, 2)))
    print('za: ', math.ceil(math.log(za, 2)))
    print('zb: ', math.ceil(math.log(abs(zb), 2)))

    commitment = [C.x, C.y]
    proof = [[Ca.x, Ca.y], [Cb.x, Cb.y], ch.BigNum(f).to_tuple(), ch.BigNum(za).to_tuple(), ch.BigNum(zb).to_tuple()]
    # print('commitment:', commitment)
    # print('proof:', proof)

    # Verify the proof
    left, right, check1, check2 = proof_verifier.verify(commitment, proof)
    #print('left:', left)
    print('right:', right)
    print('check1:', check1)
    print('check2:', check2)

    left = ch.ECC_mul(x, C) + Ca
    right = ch.ECC_commit(f, za)
    #print(f'Actual left: {left.x}, {left.y}')
    print(f'Actual right: {right.x}, {right.y}')

    # left = ch.ECC_mul(x-f, C) + Cb
    # right = ch.ECC_commit(0, zb)
    # print(f'Actual left: {left.x}, {left.y}')
    # print(f'Actual right: {right.x}, {right.y}')
    # print(f'Point at infinity: {G.point_at_infinity().x}, {G.point_at_infinity().y}')

