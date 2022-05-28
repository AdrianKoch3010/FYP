from eth_utils import to_tuple
from brownie import SigmaProofVerifier, ECC, EllipticCurve, BigNum, accounts, network, config
from web3 import Web3
from scripts import helpful_functions as hf
from scripts import crypto_helper as ch
from Crypto.Random import random
from scripts import sigma_proof as sp
import math

def deploy():
    account = hf.get_account()

    pub_source = publish_source=config['networks'][network.show_active()]['verify']
    # deploy the proof verifier
    proof_verifier = SigmaProofVerifier.deploy({'from': account}, publish_source=pub_source)
    print(f"Deployed ProofVerifier to address: {proof_verifier.address}")
    return proof_verifier


def main():
    # Deploy the contract
    proof_verifier = deploy()

    # Create 4 commitments, one of which is a commitment to 0
    generate_new = False

    # Create a list of commitments, one of which is a commitment to 0
    commitments = []
    l = 2
    n = 2
    N = 2**n
    r_0_commitment = 0
    assert l < N, "l must be less than N"
    assert N == 2**math.ceil(math.log(N, 2)), "N must be a power of 2"

    for i in range(N):
        if i == l:
            m = 0
        else:
            m = random.randint(2, ch.p-2) if generate_new else (i + 234) * 5672
        r = random.randint(2, ch.p-2) if generate_new else (i + 9876) * 987654321
        r_0_commitment = r if i == l else r_0_commitment
        commitments.append(ch.ECC_commit(m, r))

    # Create a proof
    proof = sp.generate_proof(commitments, 45, l, r_0_commitment)

    # Verify the proof on chain
    # Generate commitment tuples
    commitments_tup = []
    for point in commitments:
        commitments_tup.append([point.x, point.y])

    #print(commitment_tuples)

    # for item in proof.to_tuple():
    #     print(item)
    #     print()

    # Cl_tup = []
    # Ca_tup = []
    # Cb_tup = []
    # Cd_tup = []
    # # check that Cl, Ca, Cb, Cd are the same length
    # assert len(proof.commitment.Cl) == len(proof.commitment.Ca) == len(proof.commitment.Cb) == len(proof.commitment.Cd)
    # for i in range(len(proof.commitment.Cl)):
    #     point = [proof.commitment.Cl[i].x, proof.commitment.Cl[i].y]
    #     Cl_tup.append(point)
    #     point = [proof.commitment.Ca[i].x, proof.commitment.Ca[i].y]
    #     Ca_tup.append(point)
    #     point = [proof.commitment.Cb[i].x, proof.commitment.Cb[i].y]
    #     Cb_tup.append(point)
    #     point = [proof.commitment.Cd[i].x, proof.commitment.Cd[i].y]
    #     Cd_tup.append(point)
        
        
    # # F, Za, Zb, zd must be converted to big numbers
    # F_tup = []
    # Za_tup = []
    # Zb_tup = []
    # for num in proof.response.F:
    #     F_tup.append(ch.BigNum(num).to_tuple())
    # for num in proof.response.Za:
    #     Za_tup.append(ch.BigNum(num).to_tuple())
    # for num in proof.response.Zb:
    #     Zb_tup.append(ch.BigNum(num).to_tuple())

    # zd_tup = ch.BigNum(proof.response.zd).to_tuple()

    #result = proof_verifier.verify(proof.to_tuple(), commitment_tuples)
    result = proof_verifier.verify(commitments_tup, proof.to_tuple())
    print(f"Proof verified: {result}")

    # # Verify the proof
    # proof_valid, msg = sp.verify_proof(45, commitments, proof)
    # print("The proof is valid:", proof_valid)
    # print("Message:", msg)