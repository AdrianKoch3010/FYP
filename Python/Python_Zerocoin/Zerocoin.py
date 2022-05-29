from Crypto.Random import random
from HelperFunctions import *
from ZK_Proof import *
import math
from typing import Tuple


class Coin:
    # C is the list of coin commitments on the blockchain
    def __init__(self, l: int):
        self.l = l
        self.mint()

    # l is the index of the coin in the list of commitments
    def mint(self):
        r = random.randint(2, p-2)
        S = random.randint(2, p-2)
        c = ECC_commit(S, r)
        self.r = r
        self.S = S
        self.c = c

class Blockchain:
    def __init__(self):
        self.C = []
        self.spend_coins = []
    
    def mint_coin(self) -> Coin:
        # Add the coin commitment to the blockchain
        # and remember the index l
        coin = Coin(len(self.C))
        self.C.append(coin.c)
        return coin

    def spend_coin(self, coin: Coin) -> Tuple[SigmaProof, int]:
        # Temporary pad the list of commitments to a power of 2
        C_padded, _, _ = pad_commitments(self.C)

        # Homomorphically subtract S from the commitments
        commitments = []
        for comm in C_padded:
            commitments.append(comm + -ECC_commit(coin.S, 0))

        proof = generate_proof(commitments, coin.S, coin.l, coin.r)
        return proof, coin.S

    def verify_spend(self, S: int, proof: SigmaProof) -> Tuple[bool, str]:
        # check that this coin has not been spent
        if S in self.spend_coins:
            return False, "Coin has already been spent"

        # Temporary pad the list of commitments to a power of 2
        C_padded, _, _ = pad_commitments(self.C)

        # Homomorphically subtract S from the commitments
        commitments = []
        for comm in C_padded:
            commitments.append(comm + -ECC_commit(S, 0))
        
        proof_valid, msg = verify_proof(S, commitments, proof)
        if proof_valid:
            self.spend_coins.append(S)
            print("Coin {S} has been spent".format(S = S))
        
        return proof_valid, msg
        



#The main program
if __name__ == "__main__":
    # Create a blockchain
    blockchain = Blockchain()

    # Mint some coins
    coins = [blockchain.mint_coin() for i in range(1)]
    blockchain.C.append(ECC.EccPoint(0, 0))

    # Spend the coin
    proof, S = blockchain.spend_coin(coins[0])

    # Verify the spend
    proof_valid, msg = blockchain.verify_spend(S, proof)
    print("The proof is valid:", proof_valid)
    print("Message:", msg)
