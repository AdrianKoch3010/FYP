// contracts/ProofVerifier.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./P256.sol";


contract ProofVerifier {

    // Constructor
    constructor() {
    }

    struct Proof {
        ECC.Point c_a;
        ECC.Point c_b;
        int256 f;
        int256 z_a;
        int256 z_b;
    }

    //function verify(ECC.Point memory commitment, Proof memory proof) public pure returns (bool, bool) {
    function verify(ECC.Point memory commitment, Proof memory proof) public pure returns (ECC.Point memory, ECC.Point memory, bool, bool) {
        // check1 = ECC_mul(x, C) + Ca == ECC_commit(f, za)
        // check2 = ECC_mul(x-f, C) + Cb == ECC_commit(0, zb)

        // Compute the challenge x
        // uint256 x = proof.c_a + proof.c_b;
        int256 x = 42;

        ECC.Point memory left = ECC.mul(x, commitment);
        left = ECC.add(left, proof.c_a);
        ECC.Point memory right = ECC.commit(proof.f, proof.z_a);
        bool check1 = ECC.isEqual(left, right);

        left = ECC.mul(x - proof.f, commitment);
        left = ECC.add(left, proof.c_b);
        //right = ECC.commit(0, proof.z_b);
        right = ECC.mul(proof.z_b, ECC.H());
        bool check2 = ECC.isEqual(left, right);

        return (left, right, check1, check2);

        // Check whether the commitment is on the curve
        //return ECC.isOnCurve(commitment);
    }
}
