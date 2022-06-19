// contracts/BigNum.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

library BigNum {
    
    struct instance {
        uint128[] val;
        bool neg;
    }

    uint256 constant LOWER_MASK = 2**128 - 1;
    //uint256 constant PRIME = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff;
    uint256 constant PRIME = 0x83b4f95d30d4f5c4d271f66f220b41547ad121eefbf8d2ab745e5cefd2ef3123;

    function _new(int128 num) internal pure returns (instance memory) {
        instance memory ret;
        ret.val = new uint128[](1);
        if (num < 0) {
            ret.neg = true;
            ret.val[0] = uint128(-num);
        } else {
            ret.neg = false;
            ret.val[0] = uint128(num);
        }
        return ret;
    }

    function addInternal(uint128[] memory max, uint128[] memory min) internal pure returns (uint128[] memory) {

        // TODO: Only add 1 if overflow
        uint128[] memory result = new uint128[](max.length + 1);
        uint256 carry = 0;

        for (uint i = 0; i < max.length; i++) {
            uint256 intermediate = 0;
            if (i < min.length)
                intermediate = uint256(max[i]) + uint256(min[i]) + carry;
            else
                intermediate = uint256(max[i]) + carry;

            uint128 lower = uint128(intermediate & LOWER_MASK);
            carry = intermediate >> 128;

            result[i] = lower;
        }

        // if there remains a carry, add it to the result
        if (carry > 0) {
            result[result.length - 1] = uint128(carry);
        // Otherwise get rid of the extra bit
        }
        else {
            // resullt.length--
            assembly { mstore(result, sub(mload(result), 1)) }
        }
        return result;
    }

    function subInternal(uint128[] memory max, uint128[] memory min) internal pure returns (uint128[] memory) {
        
        uint128[] memory result = new uint128[](max.length);
        int256 carry = 0;

        for (uint i = 0; i < max.length; i++) {
            int256 intermediate = 0;
            if (i < min.length)
                intermediate = int256(uint256(max[i])) - int256(uint256(min[i])) - carry;
            else
                intermediate = int256(uint256(max[i])) - carry;

            if (intermediate < 0) {
                intermediate += 2**128;
                carry = 1;
            } else {
                carry = 0;
            }

            result[i] = uint128(uint256(intermediate));
        }

        // Clean up leading zeros
        while (result.length > 1 && result[result.length - 1] == 0)
            // result.length--;
            assembly { mstore(result, sub(mload(result), 1)) }


        return result;
    }

    function mulInternal(uint128[] memory left, uint128[] memory right) internal pure returns (uint128[] memory) {
        uint128[] memory result = new uint128[](left.length + right.length);
       
        // calculate left[i] * right
        for (uint256 i = 0; i < left.length; i++) {
            uint256 carry = 0;

            // calculate left[i] * right[j]
            for (uint256 j = 0; j < right.length; j++) {
                // Multiply with current digit of first number and add result to previously stored result at current position.
                uint256 tmp = uint256(left[i]) * uint256(right[j]);

                uint256 tmpLower = tmp & LOWER_MASK;
                uint256 tmpUpper = tmp >> 128;

                // Add both tmpLower and tmpHigher to the correct positions and take care of the carry
                uint256 intermediateLower = tmpLower + uint256(result[i + j]);
			    result[i + j] = uint128(intermediateLower & LOWER_MASK);
			    uint256 intermediateCarry = intermediateLower >> 128;

			    uint256 intermediateUpper = tmpUpper + uint256(result[i + j + 1]) + intermediateCarry + carry;
			    result[i + j + 1] = uint128(intermediateUpper & LOWER_MASK);
			    carry = intermediateUpper >> 128;
            }
        }
        // Get rid of leading zeros
        while (result.length > 1 && result[result.length - 1] == 0)
            // result.length--;
            assembly { mstore(result, sub(mload(result), 1)) }

        return result;
    }

    // Only compares absolute values
    function compare(uint128[] memory left, uint128[] memory right) internal pure returns(int)
    {
        if (left.length > right.length)
            return 1;
        if (left.length < right.length)
            return -1;
        
        // From here on we know that both numbers are the same bit size
	    // Therefore, we have to check the bytes, starting from the most significant one
        for (uint i = left.length; i > 0; i--) {
            if (left[i-1] > right[i-1])
                return 1;
            if (left[i-1] < right[i-1])
                return -1;
        }

        // Check the least significant byte
        if (left[0] > right[0])
            return 1;
        if (left[0] < right[0])
            return -1;
        
        // Only if all of the bytes are equal, return 0
        return 0;
    }

    function add(instance memory left, instance memory right) internal pure returns (instance memory)
    {
        int cmp = compare(left.val, right.val);

        if (left.neg || right.neg) {
            if (left.neg && right.neg) {
                if (cmp > 0)
                    return instance(addInternal(left.val, right.val), true);
                else
                    return instance(addInternal(right.val, left.val), true);
            }
            else {
                if (cmp > 0)
                    return instance(subInternal(left.val, right.val), left.neg);
                else
                    return instance(subInternal(right.val, left.val), !left.neg);
            }
        }
        else {
            if (cmp > 0)
                    return instance(addInternal(left.val, right.val), false);
                else
                    return instance(addInternal(right.val, left.val), false);
        }
    }

    // This function is not strictly neccessary, as add can be used for subtraction as well
    function sub(instance memory left, instance memory right) internal pure returns (instance memory)
    {
        int cmp = compare(left.val, right.val);

        if (left.neg || right.neg) {
            if (left.neg && right.neg) {
                if (cmp > 0)
                    return instance(subInternal(left.val, right.val), true);
                else
                    return instance(subInternal(right.val, left.val), false);
            }
            else {
                if (cmp > 0)
                    return instance(addInternal(left.val, right.val), left.neg);
                else
                    return instance(addInternal(right.val, left.val), left.neg);
            }
        }
        else {
            if (cmp > 0)
                    return instance(subInternal(left.val, right.val), false);
                else
                    return instance(subInternal(right.val, left.val), true);
        }
    }

    function mul(instance memory left, instance memory right) internal pure returns (instance memory)
    {
        if ((left.neg && right.neg) || (!left.neg && !right.neg))
            return instance(mulInternal(left.val, right.val), false);
        else
            return instance(mulInternal(left.val, right.val), true);
    }

    // Needed as there are multiple valid representations of 0
    function isZero(instance memory num) internal pure returns(bool) {
        if (num.val.length == 0) {
            return true;
        }
        else {
            // all the array items must be zero
            for (uint i = 0; i < num.val.length; i++) {
                if (num.val[i] != 0)
                    return false;
            }
        }
        return true;
    }

    // This function is inspired by https://github.com/monicanagent/cypherpoker/issues/5
    // Note: exp values must be 255 or shorter, otherwise the loop counter overflows
    // -> This isn't an issue as the function is only called with exponents that are 128 bit max
    // function modExp(uint256 base, uint256 exp) internal pure returns (uint256 result)  {
    //     result = 1;
    //     if (exp > 2**255 - 1) {
    //         for (uint count = 1; count <= exp / 2; count *= 2) {
    //             if (exp & count != 0)
    //                 result = mulmod(result, base, PRIME);
    //             base = mulmod(base, base, PRIME);
    //         }
    //         if (exp & 1 << 255 != 0)
    //             result = mulmod(result, base, PRIME);
    //     }
    //     else {
    //         for (uint count = 1; count <= exp; count *= 2) {
    //             if (exp & count != 0)
    //                 result = mulmod(result, base, PRIME);
    //             base = mulmod(base, base, PRIME);
    //         }
    //     }
    // }

    // Inspired by https://medium.com/@rbkhmrcr/precompiles-solidity-e5d29bd428c4
    function modExp(uint256 base, uint256 e) internal view returns (uint256 result) {
        assembly {
            // define pointer
            let p := mload(0x40)
            // store data assembly-favouring ways
            mstore(p, 0x20)             // Length of Base
            mstore(add(p, 0x20), 0x20)  // Length of Exponent
            mstore(add(p, 0x40), 0x20)  // Length of Modulus
            mstore(add(p, 0x60), base)  // Base
            mstore(add(p, 0x80), e)     // Exponent
            mstore(add(p, 0xa0), PRIME) // Modulus
            if iszero(staticcall(sub(gas(), 2000), 0x05, p, 0xc0, p, 0x20)) {
                revert(0, 0)
            }
            // data
            result := mload(p)
        }
    }


    // Calculates a uint256 to the power of a big number mod p
    function modExp(uint256 base, BigNum.instance memory power) internal view returns (uint256 result) {
        // 0 or 1 to the power of anything is 0 or 1 respectively
        if (base == 0 || base == 1)
            return base;

        // When calculating a negative power, we have to invert the base
        // Use Fermats little theorem to calculate the multiplicative inverse
        if (power.neg == true)
            base = modExp(base, PRIME - 2);

        result = 1;
        for (uint256 i = 0; i < power.val.length; i++) {
            uint256 tmp = base;
            // Multiply the correct power of 128
            for (uint256 j = 0; j < i; j++)
                tmp = modExp(tmp, 2**128);
            tmp = modExp(tmp, uint256(power.val[i]));
            result = mulmod(result, tmp, PRIME);
        }
    }
}