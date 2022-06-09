// contracts/Zetacoin.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./SigmaProofVerifier.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControlEnumerable.sol";
import "@openzeppelin/contracts/utils/Context.sol";

contract Zetacoin is Context, AccessControlEnumerable{
    IERC20 token;

    // The fixed amount of tokens minted and spent by each call to mint() and spend()
    uint256 constant public AMOUNT = 1000;

    // The list of commitments to (S, r) i.e. the list of coins
    // The length of this list must be a power of 2 at all times
    uint256[] coins;

    // The index of the last coin in the list
    uint256 lastIdx;

    // This is to avoid having to calculate the log_2 of the length of the list
    uint256 logCounter;

    // The list of spent serial numbers S
    // This record is kept to prevent double spending
    uint256[] spentSerialNumbers;

    // Constructor
    constructor(address tokenAddress) {
        _setupRole(DEFAULT_ADMIN_ROLE, _msgSender());
        token = IERC20(tokenAddress);
        lastIdx = 0;
        logCounter = 1;

        // The list of coins must have a minimum size of 2
        // We can't use a commitment to 0, 0 here, as the ECC library doesn't like multiplying a 0 point by a scalar
        coins.push(SigmaProofVerifier.commit(BigNum._new(42), BigNum._new(42)));
        coins.push(SigmaProofVerifier.commit(BigNum._new(42), BigNum._new(42)));
    }

    // Modifier to check token allowance
    modifier checkAllowance(uint256 amount) {
        require(token.allowance(_msgSender(), address(this)) >= amount, "The contract has not been given the necessary allowance");
        _;
    }

    // The mint function adds a commitment to the list of coins and returns its index
    // TODO: Minting should require burning some ERC20 token
    // It then ensures the list has length of a power of 2
    function mint(uint256 commitment) public checkAllowance(AMOUNT) returns(uint256 index) {
        // Deposit the amount in the contract
        token.transferFrom(_msgSender(), address(this), AMOUNT);

        index = lastIdx;
        
        // If the list is already long enough, assign the commitment to the next index
        if (lastIdx < coins.length) {
            coins[lastIdx] = commitment;
        }
        // This means, we have to extend to the next power of 2
        else {
            // Otherwise, append the commitment to the list
            coins.push(commitment);

            // Ensure the list has length of a power of 2 (fill up with some commitments)
            while (coins.length & (coins.length - 1) != 0)
                coins.push(SigmaProofVerifier.commit(BigNum._new(42), BigNum._new(42)));

            logCounter++;
        }
        lastIdx++;
    }

    // The spend function verifies the provided proof and marks the coin as spent
    // If successful, it transacts the ERC20 token to the caller
    // If the proof is invalid, the spend fails and the transaction is reverted
    function spend(uint256 serialNumber, SigmaProofVerifier.Proof memory proof) public returns(bool success) {
        // Check that the serial number has not been spent yet
        bool isSpent = false;
        for (uint256 i = 0; i < spentSerialNumbers.length && !isSpent; i++)
            isSpent = isSpent || (spentSerialNumbers[i] == serialNumber);
        require(!isSpent, "The coin with this serial number has already been spent");

        // Homorphically substract the serial number from the coins
        uint256[] memory commitments = new uint256[](coins.length);
        BigNum.instance memory serialNumberNeg = BigNum.instance(new uint128[](2), true);
        serialNumberNeg.val[0] = uint128(serialNumber & BigNum.LOWER_MASK);
        serialNumberNeg.val[1] = uint128(serialNumber >> 128);
        uint256 negExpSerialNumber = BigNum.modExp(SigmaProofVerifier.G, serialNumberNeg);
        for (uint256 i = 0; i < coins.length; i++)
            commitments[i] = mulmod(coins[i], negExpSerialNumber, BigNum.PRIME);
        
        // Check the proof
        success = SigmaProofVerifier.verify(serialNumber, commitments, logCounter, proof);
        require(success, "The proof is invalid");

        // Mark the coin as spent
        spentSerialNumbers.push(serialNumber);

        // Transfer the ERC20 token to the caller
        token.transfer(_msgSender(), AMOUNT);
    }

    function getCoins() public view returns(uint256[] memory) {
        return coins;
    }

    // Resets the state of the contract
    // Only for testing
    // TODO: Should the owner have this power? Propably in an actual scenario, no
    function reset() public {
        require(hasRole(DEFAULT_ADMIN_ROLE, _msgSender()), "Only admins can reset the contract");
        lastIdx = 0;
        logCounter = 1;
        delete coins;
        coins.push(SigmaProofVerifier.commit(BigNum._new(42), BigNum._new(42)));
        coins.push(SigmaProofVerifier.commit(BigNum._new(42), BigNum._new(42)));
        delete spentSerialNumbers;
    }

    // Return the amount of tokens currently held by the contract
    function getBalance() public view returns(uint256 balance) {
        return token.balanceOf(address(this));
    }
}