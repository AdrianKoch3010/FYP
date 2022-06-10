from Crypto.Random import random
from HelperFunctions import *
from ZK_Proof import *
import math
from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np


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
        

if __name__ == "__main__":
    length = [2**i for i in range(1, 7)]
    print(length)
    muls = [30, 49, 80, 135, 238, 238]
    adds = [17, 28, 47, 82, 149, 149]
    gas = [585811, 1315655, 3101827, 7400414]
    print(muls)
    print(adds)
    # plot muls and adds on the same axis against length
    #plt.plot(length, muls, 'r--', label='muls')
    plt.step(length, muls, 'r', label='ECC scalar multiplications', where='post')
    #plt.plot(length, adds, 'b--', label='adds')
    plt.step(length, adds, 'b', label='ECC point additions', where='post')
    plt.xlabel('length')
    plt.xticks(length)
    plt.ylabel('number of function calls')
    plt.legend()
    plt.savefig('ECC_efficiency analysis.svg')

    plt.figure()
    plt.plot(length[:-2], gas, 'r--', label='gas')
    plt.xlabel('length')
    plt.xticks(length[:-2])
    plt.ylabel('gas usage')
    plt.legend()
    plt.savefig('ECC_gas_usage.svg')

    # Have a look at this
    # https://cmdlinetips.com/2019/10/how-to-make-a-plot-with-two-different-y-axis-in-python-with-matplotlib/#:~:text=The%20way%20to%20make%20a,by%20updating%20the%20axis%20object.

# #The main program
# if __name__ == "__main__":

#     muls = []
#     adds = []

#     for length in [2, 4, 8, 16, 32, 64]:
#         # Create a blockchain
#         blockchain = Blockchain()

#         # Mint some coins
#         coins = [blockchain.mint_coin() for i in range(length)]
#         blockchain.C.append(ECC.EccPoint(0, 0))

#         # Spend the coin
#         proof, S = blockchain.spend_coin(coins[0])

#         ECC_mul.counter = 0
#         ECC_add.counter = 0
#         # Verify the spend
#         proof_valid, msg = blockchain.verify_spend(S, proof)
#         #print("The proof is valid:", proof_valid)
#         #print("Message:", msg)
#         #print("Mul counter:", ECC_mul.counter)
#         #print("Add counter:", ECC_add.counter)
#         muls.append(ECC_mul.counter)
#         adds.append(ECC_add.counter)
#     print("Muls:", muls)
#     print("Adds:", adds)
#     plt.plot(length, muls, label="Muls")
