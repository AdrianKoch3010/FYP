// contracts/ProofVerifier.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./P256.sol";


contract ProofVerifier {

    struct Proof {
        ECC.Point c_a;
        ECC.Point c_b;
        uint256 f;
        uint256 z_a;
        uint256 z_b;
    }

    function verify(ECC.Point memory commitment, Proof memory proof) public pure returns (bool valid) {
        // check1 = ECC_mul(x, C) + Ca == ECC_commit(f, za)
        // check2 = ECC_mul(x-f, C) + Cb == ECC_commit(0, zb)

        // Compute the challenge x
        // uint256 x = proof.c_a + proof.c_b;
        uint256 x = 42;

        ECC.Point memory left = ECC.mul(x, commitment);
        left = ECC.add(left, proof.c_a);
        ECC.Point memory right = ECC.commit(proof.f, proof.z_a);
        bool check1 = ECC.isEqual(left, right);

        left = ECC.mul(x - proof.f, commitment);
        left = ECC.add(left, proof.c_b);
        right = ECC.commit(0, proof.z_b);
        bool check2 = ECC.isEqual(left, right);

        return check1 && check2;
    }
}
