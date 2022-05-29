// contracts/SimpleProofVerifier.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./P256.sol";
// import "./BigNum.sol";


contract SimpleProofVerifier {

    // Constructor
    constructor() {
    }

    struct Proof {
        ECC.Point c_a;
        ECC.Point c_b;
        BigNum.instance f;
        BigNum.instance z_a;
        BigNum.instance z_b;
    }

    function addBig(BigNum.instance memory a, BigNum.instance memory b) public pure returns (BigNum.instance memory) {
        return BigNum.add(a, b);
    }

    function subBig(BigNum.instance memory a, BigNum.instance memory b) public pure returns (BigNum.instance memory) {
        return BigNum.sub(a, b);
    }

    function mulBig(BigNum.instance memory a, BigNum.instance memory b) public pure returns (BigNum.instance memory) {
        return BigNum.mul(a, b);
    }

    function testEccMul(BigNum.instance memory scalar, ECC.Point memory point) public pure returns (ECC.Point memory) {
        return ECC.mul(scalar, point);
    }

    //function verify(ECC.Point memory commitment, Proof memory proof) public pure returns (bool, bool) {
    function verify(ECC.Point memory commitment, Proof memory proof) public pure returns (ECC.Point memory, ECC.Point memory, bool, bool) {
        // check1 = ECC_mul(x, C) + Ca == ECC_commit(f, za)
        // check2 = ECC_mul(x-f, C) + Cb == ECC_commit(0, zb)

        // Compute the challenge x
        //int256 x = 42;
        BigNum.instance memory x = BigNum.instance(new uint128[](2), false);
        x.val[0] = 123456789;
        x.val[1] = 987654321;

        ECC.Point memory left = ECC.mul(x, commitment);
        left = ECC.add(left, proof.c_a);
        ECC.Point memory right = ECC.commit(proof.f, proof.z_a);
        bool check1 = ECC.isEqual(left, right);

        left = ECC.mul(BigNum.sub(x, proof.f), commitment);
        left = ECC.add(left, proof.c_b);
        //right = ECC.commit(0, proof.z_b);
        right = ECC.mul(proof.z_b, ECC.H());
        bool check2 = ECC.isEqual(left, right);

        return (left, right, check1, check2);
    }
}
