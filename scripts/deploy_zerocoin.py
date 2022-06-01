from eth_utils import to_tuple
from brownie import Zerocoin, DeltaToken, network, config
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
        serial_number = random.randint(2, ch.p // 4)
        #serial_number = 0
        commitment = ch.commit(serial_number, blinding_factor)
        self.blinding_factor = blinding_factor
        self.serial_number = serial_number
        self.commitment = commitment

def deployDeltaToken():
    account = hf.get_account()

    pub_source = publish_source=config['networks'][network.show_active()]['verify']
    # deploy the delta token with an initial supply of 1000 tokens
    deltaToken = DeltaToken.deploy(100000, {'from': account}, publish_source=pub_source)
    print(f"Deployed DeltaToken to address: {deltaToken.address}")
    return deltaToken

def deployZerocoin(ERC20_address):
    account = hf.get_account()

    pub_source = publish_source=config['networks'][network.show_active()]['verify']
    # deploy the zerocoin contract
    zerocoin = Zerocoin.deploy(ERC20_address, {'from': account}, publish_source=pub_source)
    print(f"Deployed Zerocoin to address: {zerocoin.address}")
    return zerocoin


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
        commitments.append(ch.commit(m, r))
    return commitments, r_0_commitment


def mint_coin(zerocoin_contract):
    coin = Coin()
    # When calling the function, the state of the blockchain is not altered, just returns the index
    index = zerocoin_contract.mint.call(coin.commitment)
    # When the mint function is called as a transaction, the state of the blockchain is altered
    zerocoin_contract.mint(coin.commitment, {'from': hf.get_account()})
    print(f"Minted coin {coin.serial_number} at index {index}")
    coin.position_in_coins = int(index)
    return coin

def spend_coin(zerocoin_contract, coin: Coin):
    # Get the list of coins
    result = zerocoin_contract.getCoins()
    coins = []
    for comm in result:
        coins.append(comm)
    
    # for c in coins:
    #     print(f'Coin: {c}')

    # Homomorphically subtract the serial number from the coin commitments
    commitments = []
    for comm in coins:
        commitments.append(comm * pow(ch.commit(coin.serial_number, 0), -1, ch.p) % ch.p)

    # proof = sp.generate_proof(commitments, coin.serial_number, coin.position_in_coins, coin.blinding_factor)
    proof = sp.generate_proof(commitments, coin.serial_number, coin.position_in_coins, coin.blinding_factor)
    print(f"Generated proof for spending coin {coin.serial_number}")

    tx = zerocoin_contract.spend(coin.serial_number, proof.to_tuple(), {'from': hf.get_account()})
    tx.wait(1)
    print(f"Spent coin {coin.serial_number} at index {coin.position_in_coins}")

def main():
    # Deploy the contracts
    deltaToken = deployDeltaToken()
    #deltaToken = DeltaToken[-1]
    zerocoin = deployZerocoin(deltaToken.address)
    #zerocoin = Zerocoin[-1]

    # Add allowance for the zerocoin contract to spend the delta token
    # This allows the zerocoin contract to transfer tokens from the caller in the mint function
    deltaToken.approve(zerocoin.address, 10000, {'from': hf.get_account()})

    # Get the balance of the zerocoin contract
    balance = zerocoin.getBalance()
    print(f"Balance of zerocoin contract: {balance}")

    # Mint 7 coins
    coins = []
    for i in range(3):
        coins.append(mint_coin(zerocoin))
        # Get the balance of the zerocoin contract
        balance = zerocoin.getBalance()
        print(f"Balance of zerocoin contract: {balance}")


    # Spend a random coin
    coin = coins[random.randint(0, len(coins)-1)]
    print(f"\n\nSpending coin {coin.serial_number}...")
    spend_coin(zerocoin, coin)

    # Get the balance of the zerocoin contract
    balance = zerocoin.getBalance()
    print(f"Balance of zerocoin contract: {balance}")

    # # Spend the coins in reverse order
    # for coin in reversed(coins):
    #     print(f"\n\nSpending coin {coin.serial_number}...")
    #     spend_coin(zerocoin, coin)

    # # Reset the contract
    # zerocoin.reset({'from': hf.get_account()})

    # # Mint 3 coins
    # coins = []
    # for i in range(3):
    #     coins.append(mint_coin(zerocoin))

    # # Spend the coins in the same order
    # for coin in coins:
    #     print(f"\n\nSpending coin {coin.serial_number}...")
    #     spend_coin(zerocoin, coin)