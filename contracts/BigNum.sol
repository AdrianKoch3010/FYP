// contracts/BigNum.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

library BigNum {
    
    struct instance {
        uint128[] val;
        bool neg;
    }

    uint256 constant public LOWER_MASK = 2**128 - 1;

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
}