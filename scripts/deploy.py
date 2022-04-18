from helpful_functions import *
from brownie import DeltaToken, accounts, network, config
from web3 import Web3


def deploy():
    account = get_account()
    delta_token = DeltaToken.deploy({'from': account}, publish_source=config['networks'][network.show_active()]['verify'])
    print(f"Deployed DeltaToken to address: {delta_token.address}")


def main():
    deploy()