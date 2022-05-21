from brownie import DeltaToken, accounts, network, config
from web3 import Web3
from scripts import helpful_functions as hf

def deploy():
    account = hf.get_account()
    initial_supply = 1000 * 10**18
    delta_token = DeltaToken.deploy(initial_supply, {'from': account}, publish_source=config['networks'][network.show_active()]['verify'])
    print(f"Deployed DeltaToken to address: {delta_token.address}")


def main():
    # Deploy the contract
    deploy()

    # Get the supply
    supply = DeltaToken[-1].totalSupply() / 10**18
    print(f"Total supply: {supply}")