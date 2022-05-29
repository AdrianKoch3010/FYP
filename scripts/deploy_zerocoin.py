from eth_utils import to_tuple
from brownie import Zerocoin, network, config
from web3 import Web3
from scripts import helpful_functions as hf
from scripts import crypto_helper as ch
from scripts import sigma_proof as sp
from Crypto.Random import random
import math

class Coin:
    # C is the list of coin commitments on the blockchain
    def __init__(self):
        self.position_in_coins = None
        self.mint()

    # l is the index of the coin in the list of commitments
    def mint(self):
        blinding_factor = random.randint(2, ch.p-2)
        # // 4 --> make sure S does not flip to negative when converting to signed int256
        #serial_number = random.randint(2, ch.p // 4)
        serial_number = 0
        commitment = ch.ECC_commit(serial_number, blinding_factor)
        self.blinding_factor = blinding_factor
        self.serial_number = serial_number
        self.commitment = commitment

def deploy():
    account = hf.get_account()

    pub_source = publish_source=config['networks'][network.show_active()]['verify']
    # deploy the proof verifier
    proof_verifier = Zerocoin.deploy({'from': account}, publish_source=pub_source)
    print(f"Deployed Zerocoin to address: {proof_verifier.address}")
    return proof_verifier

def create_commitments(n: int, l: int, generate_new = True):
    # Create a list of commitments, one of which is a commitment to 0
    #generate_new = True
    commitments = []
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
    return commitments, r_0_commitment


def mint_coin(zerocoin_contract):
    coin = Coin()
    zerocoin_contract.mint([coin.commitment.x, coin.commitment.y], {'from': hf.get_account()})
    index = zerocoin_contract.mint.call([coin.commitment.x, coin.commitment.y])
    print(f"Minted coin {coin.serial_number} at index {index}")
    coin.position_in_coins = int(index)
    return coin

def spend_coin(zerocoin_contract, coin: Coin):
    # Get the list of coins
    commitment_tuples = zerocoin_contract.getCoins()
    coins = []
    for commitment_tuple in commitment_tuples:
        coins.append(ch.ECC.EccPoint(commitment_tuple[0], commitment_tuple[1]))
    
    for c in coins:
        print(f'Coin: {c.x} {c.y}')

    # Homomorphically subtract the serial number from the coin commitments
    # commitments = []
    # for comm in C_padded:
    #     commitments.append(comm + -ch.ECC_commit(coin.serial_number, 0))

    # proof = sp.generate_proof(commitments, coin.serial_number, coin.position_in_coins, coin.blinding_factor)
    proof = sp.generate_proof(coins, coin.serial_number, coin.position_in_coins, coin.blinding_factor)
    print(f"Generated proof for spending coin {coin.serial_number}")

    tx = zerocoin_contract.spend(coin.serial_number, proof.to_tuple(), {'from': hf.get_account()})
    tx.wait(1)
    print(f"Spent coin {coin.serial_number} at index {coin.position_in_coins}")

def main():
    # Deploy the contract
    #zerocoin = deploy()
    zerocoin = Zerocoin[-1]

    # Mint a coin
    coin = mint_coin(zerocoin)

    # Spend the coin
    spend_coin(zerocoin, coin)

# def main():
#     # Deploy the contract
#     proof_verifier = deploy()
#     #proof_verifier = SigmaProofVerifier[-1]

#     # Create commitments
#     n = 4
#     l = 4
#     commitments, r_0_commitment = create_commitments(n, l, generate_new=True)

#     # Create a proof
#     proof = sp.generate_proof(commitments, 42, l, r_0_commitment)
    

#     # # Verify the proof off-chain
#     # print("Verifying proof off-chain...")
#     # proof_valid, msg = sp.verify_proof(42, commitments, proof)
#     # print("The proof is valid:", proof_valid)
#     # print("Message:", msg)

#     # Verify the proof on chain
#     print("Verifying proof on-chain...")
#     # Generate commitment tuples
#     commitments_tup = []
#     for point in commitments:
#         commitments_tup.append([point.x, point.y])

#     result = proof_verifier.verify(commitments_tup, n, proof.to_tuple())
#     print(f"Verification result: {result}")

#     # result = proof_verifier.verify.transact(commitments_tup, n, proof.to_tuple(), {'from': hf.get_account(), 'gas_limit': 30000000})
#     # print(f"Verification result: {result.info()}")
