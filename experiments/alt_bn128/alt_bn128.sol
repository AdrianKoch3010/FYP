// contracts/alt_bn128.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./BigNum.sol";


library alt_bn128 {

    uint256 constant FIELD_ORDER = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47;

    struct Point {
        uint256 x;
        uint256 y;
    }

    // Paramters taken from https://github.com/ConsenSys/anonymous-zether
    function G() internal pure returns (Point memory) {
        return Point(0x077da99d806abd13c9f15ece5398525119d11e11e9836b2ee7d23f6159ad87d4, 0x01485efa927f2ad41bff567eec88f32fb0a0f706588b4e41a8d587d008b7f875);
    }

    // Paramters taken from https://github.com/ConsenSys/anonymous-zether
    function H() internal pure returns (Point memory) {
        return Point(0x01b7de3dcf359928dd19f643d54dc487478b68a5b2634f9f1903c9fb78331aef, 0x2bda7d3ae6a557c716477c108be0d0f94abc6c4dc6b1bd93caccbcceaaa71d6b);
    }

    function add(Point memory left, Point memory right) internal view returns (Point memory result) {
        assembly {
            let m := mload(0x40)
            mstore(m, mload(left))
            mstore(add(m, 0x20), mload(add(left, 0x20)))
            mstore(add(m, 0x40), mload(right))
            mstore(add(m, 0x60), mload(add(right, 0x20)))
            if iszero(staticcall(gas(), 0x06, m, 0x80, result, 0x40)) {
                revert(0, 0)
            }
        }
    }

    function mul(Point memory point, uint256 s) internal view returns (Point memory result) {
        assembly {
            let m := mload(0x40)
            mstore(m, mload(point))
            mstore(add(m, 0x20), mload(add(point, 0x20)))
            mstore(add(m, 0x40), s)
            if iszero(staticcall(gas(), 0x07, m, 0x60, result, 0x40)) {
                revert(0, 0)
            }
        }
    }

    function inv(Point memory point) internal pure returns (Point memory) {
        return Point(point.x, FIELD_ORDER - point.y); // p.y should already be reduced mod P?
    }

    function isEqual(Point memory left, Point memory right) internal pure returns (bool) {
        return left.x == right.x && left.y == right.y;
    }

    // Overload of the mul function taking a BigNum arguments
    function mul(BigNum.instance memory scalar, Point memory point) internal view returns(Point memory result) {
        // 0 * something = point at infinity
        if (BigNum.isZero(scalar))
            return Point(0, 0);

        result = Point(0, 0);
        Point memory init = point;
        // When multiplying by a negative number, we have to invert the point
        if (scalar.neg)
            init = inv(point);

        for (uint256 i = 0; i < scalar.val.length; i++) {
            Point memory tmp = init;
            // Multiply by the correct power of 128
            for (uint256 j = 0; j < i; j++) {
                tmp = mul(tmp, 2**128);
            }
            if (scalar.val[i] != 0)
                tmp = mul(tmp, uint256(scalar.val[i]));
            else
                tmp = Point(0, 0);
            
            result = add(result, tmp);
        }
    }

    function pointAtInf() internal pure returns (Point memory) {
        // uint256 x;
        // uint256 y;
        // (x, y) = EllipticCurve.toAffine(0, 1, 0, PP);
        return Point(0, 0);
    }

    function commit(int256 m, int256 r) internal view returns (Point memory) {
        // This will be incorrect
        Point memory left = mul(G(), uint256(m));
        Point memory right = mul(H(), uint256(r));
        return add(left, right);
    }

    // Overload of the commit function taking BigNum arguments
    function commit(BigNum.instance memory m, BigNum.instance memory r) internal view returns (Point memory) {
        Point memory left = mul(m, G());
        Point memory right = mul(r, H());
        return add(left, right);
    }

}