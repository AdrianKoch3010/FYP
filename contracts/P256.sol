// contracts/P256.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./EllipticCurve.sol";
import "./BigNum.sol";


library ECC 
{
    // uint256 constant GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798;
    // uint256 constant GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8;
    // uint256 constant AA = 0;
    // uint256 constant BB = 7;
    // uint256 constant PP = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F;

    uint256 constant GX = 0xc6147090dc789cd1827476f06c4080f727117427feb1ea10f5f58a1b8f26a646;
    uint256 constant GY = 0x9a8048d281edee5f5d7859ede6c7000ed420b55ac4604558c95b5e6f32de2276;
    uint256 constant HX = 0x418ed4f85c649bf336d9e213337bfbb8d5e203c6ec1ad59d6c975e66b358bf3b;
    uint256 constant HY = 0xa479d9ab22e0c2e0fdf9659656b9efcd8f24da23cfc1eedfa852df9a1e621309;
    uint256 constant AA = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc;
    uint256 constant BB = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b;
    uint256 constant PP = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff;

    struct Point {
        uint256 x;
        uint256 y;
    }

    function G() public pure returns (Point memory) {
        return Point(GX, GY);
    }

    // TODO: calculate values for H
    function H() public pure returns (Point memory) {
        return Point(HX, HY);
    }

    function isEqual(Point memory left, Point memory right) public pure returns (bool) {
        return left.x == right.x && left.y == right.y;
    }

    function inv(Point memory point) public pure returns (Point memory) {
        uint256 x;
        uint256 y;
        (x, y) = EllipticCurve.ecInv(point.x, point.y, PP);
        return Point(x, y);
    }

    function add(Point memory left, Point memory right) public pure returns (Point memory) {
        uint256 x;
        uint256 y;
        (x, y) = EllipticCurve.ecAdd(left.x, left.y, right.x, right.y, AA, PP);
        return Point(x, y);
    }

    function sub(Point memory left, Point memory right) public pure returns (Point memory) {
        uint256 x;
        uint256 y;
        (x, y) = EllipticCurve.ecSub(left.x, left.y, right.x, right.y, AA, PP);
        return Point(x, y);
    }

    function mul(int256 scalar, Point memory point) public pure returns (Point memory) {
        uint256 x;
        uint256 y;
        // if the scalar is negative, we have to invert the point
        if (scalar < 0) {
            uint256 xInv;
            uint256 yInv;
            (xInv, yInv) = EllipticCurve.ecInv(point.x, point.y, PP);
            (x, y) = EllipticCurve.ecMul(uint(-scalar), xInv, yInv, AA, PP);
        }
        else if (scalar > 0) {{ 
            (x, y) = EllipticCurve.ecMul(uint(scalar), point.x, point.y, AA, PP);
        }
        }
        else {
            // 0 * something = point at infinity
            x = 0;
            y = 0;
        }
        return Point(x, y);
    }

    // Overload of the mul function taking a BigNum arguments
    function mul(BigNum.instance memory scalar, Point memory point) public pure returns(Point memory) {
        // 0 * something = point at infinity
        if (BigNum.isZero(scalar))
            return Point(0, 0);

        uint256 x = 0;
        uint256 y = 0;
        uint256 xInit = point.x;
        uint256 yInit = point.y;
        // When multiplying by a negative number, we have to invert the point
        if (scalar.neg)
            (xInit, yInit) = EllipticCurve.ecInv(point.x, point.y, PP);

        for (uint256 i = 0; i < scalar.val.length; i++) {
            uint256 xTmp = xInit;
            uint256 yTmp = yInit;
            // Multiply by the correct power of 128
            for (uint256 j = 0; j < i; j++) {
                (xTmp, yTmp) = EllipticCurve.ecMul(2**128, xTmp, yTmp, AA, PP);
            }
            if (scalar.val[i] != 0)
                (xTmp, yTmp) = EllipticCurve.ecMul(uint256(scalar.val[i]), xTmp, yTmp, AA, PP);
            else
                (xTmp, yTmp) = (0, 0);
            (x, y) = EllipticCurve.ecAdd(x, y, xTmp, yTmp, AA, PP);
        }
        return Point(x, y);
    }

    function pointAtInf() public pure returns (Point memory) {
        // uint256 x;
        // uint256 y;
        // (x, y) = EllipticCurve.toAffine(0, 1, 0, PP);
        return Point(0, 0);
    }

    function commit(int256 m, int256 r) public pure returns (Point memory) {
        Point memory left = mul(m, G());
        Point memory right = mul(r, H());
        return add(left, right);
    }

    // Overload of the commit function taking BigNum arguments
    function commit(BigNum.instance memory m, BigNum.instance memory r) public pure returns (Point memory) {
        Point memory left = mul(m, G());
        Point memory right = mul(r, H());
        return add(left, right);
    }

    function isOnCurve(Point memory point) public pure returns (bool) {
        return EllipticCurve.isOnCurve(point.x, point.y, AA, BB, PP);        
    }
}

