// contracts/P256.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./EllipticCurve.sol";


// contract Secp256k1 {

//   uint256 public constant GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798;
//   uint256 public constant GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8;
//   uint256 public constant AA = 0;
//   uint256 public constant BB = 7;
//   uint256 public constant PP = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F;

// function invMod(uint256 val, uint256 p) pure public returns (uint256)
// {
//     return EllipticCurve.invMod(val,p);
// }

// function expMod(uint256 val, uint256 e, uint256 p) pure public returns (uint256)
// {
//     return EllipticCurve.expMod(val,e,p);
// }


// function getY(uint8 prefix, uint256 x) pure public returns (uint256)
// {
//     return EllipticCurve.deriveY(prefix,x,AA,BB,PP);
// }


// function onCurve(uint256 x, uint256 y) pure public returns (bool)
// {
//     return EllipticCurve.isOnCurve(x,y,AA,BB,PP);
// }

// function inverse(uint256 x, uint256 y) pure public returns (uint256, 
// uint256) {
//     return EllipticCurve.ecInv(x,y,PP);
//   }

// function subtract(uint256 x1, uint256 y1,uint256 x2, uint256 y2 ) pure public returns (uint256, uint256) {
//     return EllipticCurve.ecSub(x1,y1,x2,y2,AA,PP);
//   }

//   function add(uint256 x1, uint256 y1,uint256 x2, uint256 y2 ) pure public returns (uint256, uint256) {
//     return EllipticCurve.ecAdd(x1,y1,x2,y2,AA,PP);
//   }

// function derivePubKey(uint256 privKey) pure public returns (uint256, uint256) {
//     return EllipticCurve.ecMul(privKey,GX,GY,AA,PP);
//   }
// }

library ECC 
{
    uint256 constant GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798;
    uint256 constant GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8;
    uint256 constant AA = 0;
    uint256 constant BB = 7;
    uint256 constant PP = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F;

    struct Point {
        uint256 x;
        uint256 y;
    }

    function G() public pure returns (Point memory) {
        return Point(GX, GY);
    }

    // TODO: calculate values for H
    function H() public pure returns (Point memory) {
        return Point(GX, GY);
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

    function mul(uint256 scalar, Point memory point) public pure returns (Point memory) {
        uint256 x;
        uint256 y;
        (x, y) = EllipticCurve.ecMul(scalar, point.x, point.y, AA, PP);
        return Point(x, y);
    }

    function commit(uint256 m, uint256 r) public pure returns (Point memory) {
        Point memory left = mul(m, G());
        Point memory right = mul(r, H());
        return add(left, right);
    }
}

