from Python.Python_Zerocoin.HelperFunctions import G
from brownie import SimpleProofVerifier, ECC, EllipticCurve, BigNum, accounts, network, config
from web3 import Web3
from scripts import helpful_functions as hf
from scripts import crypto_helper as ch
from Crypto.Random import random
import math

def deploy():
    account = hf.get_account()

    pub_source = publish_source=config['networks'][network.show_active()]['verify']
    # deploy the libraries
    #EllipticCurve.deploy({'from': account}, publish_source=pub_source)
    #BigNum.deploy({'from': account}, publish_source=pub_source)
    #ECC.deploy({'from': account}, publish_source=pub_source)
    # deploy the proof verifier
    proof_verifier = SimpleProofVerifier.deploy({'from': account}, publish_source=pub_source)
    print(f"Deployed ProofVerifier to address: {proof_verifier.address}")
    return proof_verifier


def main():
    # Deploy the contract
    proof_verifier = deploy()

    # test modExp
    base = ch.g
    exponent = ch.BigNum(42)

    result = proof_verifier.testModExpBig(base, exponent.to_tuple())
    print(f"ModExp: {result}")
    print(f'Correct: {result == pow(base, exponent.to_int(), ch.p)}')

    # Attempt to verify a proof
    # proof structure:
    # ECC.Point c_a;
    # ECC.Point c_b;
    # uint256 f;
    # uint256 z_a;
    # uint256 z_b;
    
    _max = ch.p - 2
    generate_new = False

    p = ch.p
    m = 1
    r = random.randint(2, _max) if generate_new else 1556

    print('m:', m)
    print('r:', r)

    # Generate x
    #x = random.getrandbits(128)
    x = ch.BigNum([123456789, 987654321]).to_int()
    print('x:', x)

    a = random.randint(2, _max) if generate_new else 455
    s = random.randint(2, _max) if generate_new else 567
    t = random.randint(2, _max) if generate_new else 678

    f = m*x + a
    za = r*x + s
    zb = r*(x-f) + t

    print('Verifying using mod exponentials...')
    # C = m * G + r * H
    # Ca = a * G + s * H
    # Cb = (a*m) * G + t * H
    #print('c: {c.x}, {c.y}'.format(c=c))
    C = ch.commit(m, r)
    Ca = ch.commit(a, s)
    Cb = ch.commit(a*m, t)

    # print('p:', math.ceil(math.log(p, 2)))
    # print('C: ', math.ceil(math.log(C, 2)))
    # print('Ca: ', math.ceil(math.log(Ca, 2)))
    # print('Cb: ', math.ceil(math.log(Cb, 2)))
    # print('f: ', math.ceil(math.log(f, 2)))
    # print('za: ', math.ceil(math.log(za, 2)))
    # print('zb: ', math.ceil(math.log(abs(zb), 2)))

    commitment = C
    proof = [Ca, Cb, ch.BigNum(f).to_tuple(), ch.BigNum(za).to_tuple(), ch.BigNum(zb).to_tuple()]
    # print('commitment:', commitment)
    # print('proof:', proof)

    # Verify the proof
    proof_verifier.verifySimple.transact(commitment, proof)
    left, right, check1, check2 = proof_verifier.verifySimple.call(commitment, proof)
    print('left:', left)
    print('right:', right)
    print('check1:', check1)
    print('check2:', check2)

    print('Verifying using elliptic curves...')
    C = ch.ECC_commit(m, r)
    Ca = ch.ECC_commit(a, s)
    Cb = ch.ECC_commit(a*m, t)

    commitment = [C.x, C.y]
    proof = [[Ca.x, Ca.y], [Cb.x, Cb.y], ch.BigNum(f).to_tuple(), ch.BigNum(za).to_tuple(), ch.BigNum(zb).to_tuple()]

    proof_verifier.verify.transact(commitment, proof)
    left, right, check1, check2 = proof_verifier.verify.call(commitment, proof)
    print('left:', left)
    print('right:', right)
    print('check1:', check1)
    print('check2:', check2)
    



