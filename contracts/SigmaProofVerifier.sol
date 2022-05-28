// contracts/SigmaProofVerifier.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./P256.sol";
// import "./BigNum.sol";


contract SigmaProofVerifier {

    // Constructor
    constructor() {
    }

    struct SigmaProof {
        ECC.Point[] C_l;
        ECC.Point[] C_a;
        ECC.Point[] C_b;
        ECC.Point[] C_d;
        BigNum.instance[] F;
        BigNum.instance[] Z_a;
        BigNum.instance[] Z_b;
        BigNum.instance z_d;
    }

    // Check the commitments to l part 1
    function verifyProofCheck1(
        uint256 n,
        BigNum.instance memory x,
        ECC.Point[] memory C_l, 
        ECC.Point[] memory C_a,
        BigNum.instance[] memory F,
        BigNum.instance[] memory Z_a)
    internal pure returns (bool check) {
        // Declare the left and right side of the check
        ECC.Point memory left;
        ECC.Point memory right;

        // Check the commitments to l
        check = true;
        for (uint256 i = 0; i < n; i++) {
            left = ECC.mul(x, C_l[i]);
            left = ECC.add(left, C_a[i]);
            right = ECC.commit(F[i], Z_a[i]);
            check = check && ECC.isEqual(left, right);
        }
    }

    // Check the commitments to l part 2
    function verifyProofCheck2(
        uint256 n,
        BigNum.instance memory x,
        ECC.Point[] memory C_l, 
        ECC.Point[] memory C_b,
        BigNum.instance[] memory F,
        BigNum.instance[] memory Z_b)
    internal pure returns (bool check) {
        // Declare the left and right side of the check
        ECC.Point memory left;
        ECC.Point memory right;

        check = true;
        for (uint256 i = 0; i < n; i++) {
            left = ECC.mul(BigNum.sub(x, F[i]), C_l[i]);
            left = ECC.add(left, C_b[i]);
            //ECC.Point memory right = ECC.commit(0, proof.Z_b[i]);
            right = ECC.mul(Z_b[i], ECC.H());
            check = check && ECC.isEqual(left, right);
        }
    }

    // Check the commitment to 0
    function verifyProofCheck3(
        uint256 n,
        ECC.Point[] memory commitments,
        BigNum.instance memory x,
        BigNum.instance[] memory F,
        ECC.Point[] memory C_d,
        BigNum.instance memory z_d)
    internal pure returns (bool check) {
        // Declare the left and right side of the check
        ECC.Point memory left;
        ECC.Point memory right;
        uint256 N = n**2;

        ECC.Point memory leftSum = ECC.pointAtInf();
        for (uint256 i = 0; i < N; i++) {
            // Calculate the product of F_j, i_j
            BigNum.instance memory product = BigNum.instance(new uint128[](1), false);
            product.val[0] = 1;

            for (uint256 j = 0; j < n; j++) {
                uint256 i_j = i >> j & 1;
                if (i_j == 1)
                    product = BigNum.mul(product, F[j]);
                else
                    product = BigNum.mul(product, BigNum.sub(x, F[j]));
            }
            leftSum = ECC.add(leftSum, ECC.mul(product, commitments[i]));
        }

        // Calculate the sum of the other commitments
        ECC.Point memory rightSum = ECC.pointAtInf();
        BigNum.instance memory xPowk = BigNum.instance(new uint128[](1), false);
        xPowk.val[0] = 1;
        for (uint256 k = 0; k < n; k++) {
            xPowk.neg = true;
            rightSum = ECC.add(rightSum, ECC.mul(xPowk, C_d[k]));
            xPowk.neg = false;
            xPowk = BigNum.mul(xPowk, x);
        }

        left = ECC.add(leftSum, rightSum);
        // ECC.Point memory right = ECC.commit(0, proof.z_d);
        right = ECC.mul(z_d, ECC.H());
        check = ECC.isEqual(left, right);
    }

    //function verify(ECC.Point memory commitment, Proof memory proof) public pure returns (bool, bool) {
    function verify(ECC.Point[] memory commitments, SigmaProof memory proof) public pure returns (bool check1, bool check2, bool check3) {
        
        // For now, hardcode the length of the commitment list
        uint256 n = 2;

        // For now, hardcode the challenge
        BigNum.instance memory x = BigNum.instance(new uint128[](1), false);
        x.val[0] = 123456789;

        check1 = verifyProofCheck1(n, x, proof.C_l, proof.C_a, proof.F, proof.Z_a);
        check2 = verifyProofCheck2(n, x, proof.C_l, proof.C_b, proof.F, proof.Z_b);
        //check3 = verifyProofCheck3(n, commitments, x, proof.F, proof.C_d, proof.z_d);
        check3 = false;
    }
}
