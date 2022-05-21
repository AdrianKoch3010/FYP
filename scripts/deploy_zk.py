from brownie import ProofVerifier, ECC, EllipticCurve, accounts, network, config
from web3 import Web3
from scripts import helpful_functions as hf
from scripts import crypto_helper as ch
from Crypto.Random import random

def deploy():
    account = hf.get_account()

    pub_source = publish_source=config['networks'][network.show_active()]['verify']
    # deploy the libraries
    EllipticCurve.deploy({'from': account}, publish_source=pub_source)
    ECC.deploy({'from': account}, publish_source=pub_source)
    proof_verifier = ProofVerifier.deploy({'from': account}, publish_source=pub_source)
    print(f"Deployed DeltaToken to address: {proof_verifier.address}")
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

    p = ch.p
    m = 1
    r = random.randint(2, p-2)
    #m = int.from_bytes(SHA256.new(message).digest(), byteorder='big')
    #r = int.from_bytes(SHA256.new(blinding_factor).digest(), byteorder='big')
    print('m:', m)
    print('r:', r)

    #G = ECC.generate(curve='P-256').pointQ
    #H = ECC.generate(curve='P-256').pointQ

    a = random.randint(2, p-2)
    s = random.randint(2, p-2)
    t = random.randint(2, p-2)


    # C = m * G + r * H
    # Ca = a * G + s * H
    # Cb = (a*m) * G + t * H
    #print('c: {c.x}, {c.y}'.format(c=c))
    C = ch.ECC_commit(m, r)
    Ca = ch.ECC_commit(a, s)
    Cb = ch.ECC_commit(a*m, t)

    # Generate x
    #x = random.getrandbits(128)
    x = 42
    print('x:', x)

    f = m*x + a
    za = r*x + s
    zb = r*(x-f) + t

    commitment = [C.x, C.y]
    proof = [[Ca.x, Ca.y], [Cb.x, Cb.y], f, za, zb]
    print('commitment:', commitment)
    print('proof:', proof)

    # Verify the proof
    valid = proof_verifier.verify(commitment, proof)
    print('valid:', valid)