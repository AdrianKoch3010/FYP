// contracts/alt_bn128Zetacoin.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./alt_bn128SigmaProofVerifier.sol";

contract alt_bn128Zetacoin {
    // Constructor
    constructor() {
        lastIdx = 0;
        logCounter = 1;

        // The list of coins must have a minimum size of 2
        // We can't use a commitment to 0, 0 here, as the alt_bn128 library doesn't like multiplying a 0 point by a scalar
        coins.push(alt_bn128.commit(42, 42));
        coins.push(alt_bn128.commit(42, 42));
    }

    // The list of commitments to (S, r) i.e. the list of coins
    // The length of this list must be a power of 2 at all times
    alt_bn128.Point[] coins;

    // The index of the last coin in the list
    uint256 lastIdx;

    // This is to avoid having to calculate the log_2 of the length of the list
    uint256 logCounter;

    // The list of spent serial numbers S
    // This record is kept to prevent double spending
    uint256[] spentSerialNumbers;

    // The mint function adds a commitment to the list of coins and returns its index
    // TODO: Minting should require burning some ERC20 token
    // It then ensures the list has length of a power of 2
    function mint(alt_bn128.Point memory commitment) public returns(uint256 index) {
        index = lastIdx;
        
        // If the list is already long enough, assign the commitment to the next index
        if (lastIdx < coins.length) {
            coins[lastIdx] = commitment;
        }
        // This means, we have to extend to the next power of 2
        else {
            // Otherwise, append the commitment to the list
            coins.push(commitment);

            // Ensure the list has length of a power of 2 (fill up with zeros)
            while (coins.length & (coins.length - 1) != 0)
                // We can't use a commitment to 0, 0 here, as the alt_bn128 library doesn't like multiplying a 0 point by a scalar
                coins.push(alt_bn128.commit(42, 42));

            logCounter++;
        }
        lastIdx++;
    }

    // The spend function verifies the provided proof and marks the coin as spent
    // If successful, it transacts the ERC20 token to the caller
    // If the proof is invalid, the spend fails and the transaction is reverted
    function spend(uint256 serialNumber, alt_bn128SigmaProofVerifier.Proof memory proof) public returns(bool success) {
        // Check that the serial number has not been spent yet
        bool isSpent = false;
        for (uint256 i = 0; i < spentSerialNumbers.length && !isSpent; i++)
            isSpent = isSpent || (spentSerialNumbers[i] == serialNumber);
        require(!isSpent, "The coin with this serial number has already been spent");

        // Homorphically substract the serial number from the coins
        alt_bn128.Point[] memory commitments = new alt_bn128.Point[](coins.length);
        for (uint256 i = 0; i < coins.length; i++)
            // This is incorrect
            commitments[i] = alt_bn128.add(coins[i], alt_bn128.inv(alt_bn128.mul(alt_bn128.G(), serialNumber)));
            //commitments[i] = alt_bn128.sub(coins[i], alt_bn128.mul(int256(serialNumber), alt_bn128.G()));
            //commitments[i] = alt_bn128.add(coins[i], alt_bn128.inv(alt_bn128.mul(int256(serialNumber), alt_bn128.G())));
        
        // Check the proof
        success = alt_bn128SigmaProofVerifier.verify(serialNumber, commitments, logCounter, proof);
        //success = SigmaProofVerifier.verify(serialNumber, coins, logCounter, proof);
        require(success, "The proof is invalid");

        // Mark the coin as spent
        spentSerialNumbers.push(serialNumber);
    }

    function getCoins() public view returns(alt_bn128.Point[] memory) {
        return coins;
    }

    // Resets the state of the contract
    // Only for testing
    // TODO: Should the owner have this power? Propably in an actual scenario, no
    function reset() public {
        lastIdx = 0;
        logCounter = 1;
        delete coins;
        coins.push(alt_bn128.commit(42, 42));
        coins.push(alt_bn128.commit(42, 42));
        delete spentSerialNumbers;
    }
}