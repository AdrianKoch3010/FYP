from helpful_functions import *
from brownie import DeltaToken, accounts, network, config


def mint(value=10**18):
    account = get_account()
    DeltaToken.mint(accounts, value, {'from': account})
    print(f"Minted {value} to {account.address}")
    
def main():
    print('How many tokens do you want to mint?')
    value = int(input())
    mint(value * 10**18)