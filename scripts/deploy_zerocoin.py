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
    generate_new = True

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
            m = random.randint(2, ch.p-2) if generate_new else (i + 234) * 567211321231
        r = random.randint(2, ch.p-2) if generate_new else (i + 9876) * 987654321521321551235
        r_0_commitment = r if i == l else r_0_commitment
        commitments.append(ch.ECC_commit(m, r))

    # Create a proof
    proof = sp.generate_proof(commitments, 45, l, r_0_commitment)

    # Verify the proof off-chain
    print("Verifying proof off-chain...")
    proof_valid, msg = sp.verify_proof(42, commitments, proof)
    print("The proof is valid:", proof_valid)
    print("Message:", msg)

    # Verify the proof on chain
    print("Verifying proof on-chain...")
    # Generate commitment tuples
    commitments_tup = []
    for point in commitments:
        commitments_tup.append([point.x, point.y])

    result = proof_verifier.verify(commitments_tup, proof.to_tuple())
    #result = proof_verifier.verifyProofCheck3(2, ch.BigNum(123456789).to_tuple(), commitments_tup, proof.to_tuple())
    #for num in result:
        #print(ch.BigNum(num[0], num[1]).to_int())
        #print(num)
    print(f"Verification result: {result}")


    # num = ch.BigNum(123456789)
    # result = proof_verifier.testPow(num.to_tuple(), 40)
    # print(f"Proof verified: {result}")
    # res = ch.BigNum(result[0])
    # actual_res = num.to_int() ** 40
    # print(f"Actual result: {hex(actual_res)}")
    # print(f"Result: {hex(res.to_int())}")
    # print(f"Result == Actual Result: {res.to_int() == actual_res}")

    # # Verify the proof
    # proof_valid, msg = sp.verify_proof(45, commitments, proof)
    # print("The proof is valid:", proof_valid)
    # print("Message:", msg)