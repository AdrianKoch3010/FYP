// contracts/ProofVerifierTest.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./P256.sol";
// import "./BigNum.sol";


contract ProofVerifierTest {

    uint256 constant G = 3007057779649931580237598654612510797095951971612630025891176454468165002055;
    uint256 constant H = 20354936247998155748817459761265066334754915076915271771709029462851510023744;

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

    struct SimpleProof {
        uint256 c_a;
        uint256 c_b;
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

    function testEccAdd(ECC.Point memory a, ECC.Point memory b) public pure returns (ECC.Point memory) {
        return ECC.add(a, b);
    }

    function testEccMul(BigNum.instance memory scalar, ECC.Point memory point) public pure returns (ECC.Point memory) {
        return ECC.mul(scalar, point);
    }

    function testModExp(uint256 base, uint256 exponent) public view returns (uint256) {
        return BigNum.modExp(base, exponent);
    }

    function testModExpBig(uint256 base, BigNum.instance memory exponent) public view returns(uint256) {
        return BigNum.modExp(base, exponent);
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

    function verifySimple(uint256 commitment, SimpleProof memory proof) public view returns (uint256, uint256, bool, bool) {
        // check1 = pow(C, x, p) * Ca % p == commit(f, za)
        // check2 = pow(C, x-f, p) * Cb % p == commit(0, zb)

        // Compute the challenge x
        //int256 x = 42;
        BigNum.instance memory x = BigNum.instance(new uint128[](2), false);
        x.val[0] = 123456789;
        x.val[1] = 987654321;

        uint256 left = BigNum.modExp(commitment, x);
        left = mulmod(left, proof.c_a, BigNum.PRIME);
        uint256 right = mulmod(BigNum.modExp(G, proof.f), BigNum.modExp(H, proof.z_a), BigNum.PRIME);
        bool check1 = left == right;

        left = BigNum.modExp(commitment, BigNum.sub(x, proof.f));
        left = mulmod(left, proof.c_b, BigNum.PRIME);
        right = BigNum.modExp(H, proof.z_b);
        bool check2 = left == right;

        return (left, right, check1, check2);
    }
}
