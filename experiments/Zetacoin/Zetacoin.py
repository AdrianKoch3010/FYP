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
        
# 2,  3,4   5,6,7,8  9,
def plot_mul_and_gas(muls, gas):
    #plt.figure()
    font = {'family': 'serif',
            'weight': 'normal',
            'size': 20}
    plt.rc('font', **font)
    plt.rcParams['figure.figsize'] = (13, 8)
    plt.rcParams['figure.autolayout'] = True

    length = [2**i + 1 for i in range(len(muls))]
    length_ext = length + [(length[-1]-1)*2]
    gas_ext = gas + [gas[-1]]
    muls_ext = muls + [muls[-1]]
    ax1 = plt.subplot()
    ax1.set_xlabel('Anonymity set size')
    ax1.set_ylabel('Gas consumption')
    l1, = ax1.step(length_ext, gas_ext, 'tab:red', alpha=0.85, label="Gas", where="post")
    ax1.plot(length, gas, color='tab:red', ls="--", alpha=0.5, label="Gas")
    
    # Plot ECC gas consmption point
    val = 10565215
    #ax1.plot([length[0]], [val / 10], color='tab:red', ls="dotted", alpha=1.0, label="ECCGas")
    ax1.plot(2, val, marker='^', markersize=10, markeredgecolor='tab:red', markerfacecolor='tab:red', label="ECCGas")
    ax1.text(2 + 0.3, val, "ECC Gas", fontsize=20, va='center', ha='left')
    ax1.set_ylim([0, val*1.25])

    ax2 = ax1.twinx()
    # ax2.set_xlabel('length')
    ax2.set_ylabel('No. of modular exponentiations')
    l2, = ax2.step(length_ext, muls_ext, 'tab:blue', alpha=0.85, label="Mul", where="post")
    ax2.plot(length, muls, color='tab:blue', ls='--', alpha=0.5, label="Mul")
    ax2.set_ylim([0, muls[-1]*1.25])

    #plt.xticks(length_ext)
    plt.legend([l2, l1], ['No. of modular exponentiations', 'Gas consumption'])
    plt.savefig('mul_and_gas.png')

def plot_gas_and_proof_size(gas, proof_sizes):
    # Subtract 32 from the proof size
    proof_sizes = [proof_size - 32 for proof_size in proof_sizes]

    plt.figure()
    font = {'family': 'serif',
            'weight': 'normal',
            'size': 20}
    plt.rc('font', **font)
    plt.rcParams['figure.figsize'] = (13, 8)
    plt.rcParams['figure.autolayout'] = True

    length = [2**i + 1 for i in range(len(gas))]
    # length_ext = length + [(length[-1]-1)*2]
    length_ext = length + [40]
    gas_ext = gas + [gas[-1]]
    proof_sizes_ext = proof_sizes + [proof_sizes[-1]]
    ax1 = plt.subplot()
    ax1.set_xlabel('Anonymity set size')
    ax1.set_ylabel('Gas consumption')
    # Plot the actual gas consumption
    l1, = ax1.step(length_ext[:-2], gas_ext[:-2], 'tab:red', alpha=0.85, label="Gas", where="post")
    ax1.plot(length[:-1], gas[:-1], color='tab:red', ls="--", alpha=0.5, label="Gas")

    # Plot the extrapolated gas consumption
    ax1.step(length_ext[-3:], gas_ext[-3:], 'tab:red', ls=':', alpha=0.35, label="Gas", where="post")
    ax1.plot(length[-2:], gas[-2:], color='tab:red', ls="-.", alpha=0.25, label="Gas")

    ax1.set_ylim([0, gas[-1]*1.2])

    ax2 = ax1.twinx()
    ax2.set_ylabel('Proof size (bytes)')
    l2, = ax2.step(length_ext, proof_sizes_ext, 'tab:green', alpha=0.85, label="ProofSize", where="post")
    ax2.plot(length, proof_sizes, color='tab:green', ls='--', alpha=0.5, label="ProofSize")
    ax2.set_ylim([0, proof_sizes[-1]*1.1])

    #plt.xticks(length_ext)
    plt.legend([l2, l1], ['Proof size', 'Gas consumption'])
    plt.savefig('gas_and_proof_size.png')


# if __name__ == "__main__":
#     _muls = [30, 49, 80, 135, 238, 238]
#     muls = [30, 49, 80, 135]
#     adds = [17, 28, 47, 82, 149, 149]
#     gas = [585811, 1315655, 3101827, 7400414]
#     gas_extrapolated = [585811, 1315655, 3101827, 7400414, 17135561, 32711796]
#     proof_sizes = [802, 1250, 1714, 2162, 2594, 3042]

#     plot_mul_and_gas(muls, gas)

#     plot_gas_and_proof_size(gas_extrapolated, proof_sizes)



    
    # Have a look at this
    # https://cmdlinetips.com/2019/10/how-to-make-a-plot-with-two-different-y-axis-in-python-with-matplotlib/#:~:text=The%20way%20to%20make%20a,by%20updating%20the%20axis%20object.

#The main program
if __name__ == "__main__":

    muls = []
    adds = []

    for length in [2 ]:#, 4, 8, 16, 32, 64]:
        # Create a blockchain
        blockchain = Blockchain()

        # Mint some coins
        coins = [blockchain.mint_coin() for i in range(length)]
        blockchain.C.append(ECC.EccPoint(0, 0))

        # Spend the coin
        proof, S = blockchain.spend_coin(coins[0])

        ECC_mul.counter = 0
        ECC_add.counter = 0
        # Verify the spend
        proof_valid, msg = blockchain.verify_spend(S, proof)
        #print("The proof is valid:", proof_valid)
        #print("Message:", msg)
        #print("Mul counter:", ECC_mul.counter)
        #print("Add counter:", ECC_add.counter)
        muls.append(ECC_mul.counter)
        adds.append(ECC_add.counter)
    print("Muls:", muls)
    print("Adds:", adds)
    plt.plot(length, muls, label="Muls")
