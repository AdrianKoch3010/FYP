// contracts/alt_bn128SigmaProofVerifier.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./alt_bn128.sol";


library alt_bn128SigmaProofVerifier {

    struct Proof {
        alt_bn128.Point[] C_l;
        alt_bn128.Point[] C_a;
        alt_bn128.Point[] C_b;
        alt_bn128.Point[] C_d;
        BigNum.instance[] F;
        BigNum.instance[] Z_a;
        BigNum.instance[] Z_b;
        BigNum.instance z_d;
    }

    // Check the commitments to l part 1
    function verifyProofCheck1(
        uint256 n,
        BigNum.instance memory x,
        alt_bn128.Point[] memory C_l, 
        alt_bn128.Point[] memory C_a,
        BigNum.instance[] memory F,
        BigNum.instance[] memory Z_a)
    internal view returns (bool check) {
        // Declare the left and right side of the check
        alt_bn128.Point memory left;
        alt_bn128.Point memory right;

        // Check the commitments to l
        check = true;
        for (uint256 i = 0; i < n; i++) {
            left = alt_bn128.mul(x, C_l[i]);
            left = alt_bn128.add(left, C_a[i]);
            right = alt_bn128.commit(F[i], Z_a[i]);
            check = check && alt_bn128.isEqual(left, right);
        }
    }

    // Check the commitments to l part 2
    function verifyProofCheck2(
        uint256 n,
        BigNum.instance memory x,
        alt_bn128.Point[] memory C_l, 
        alt_bn128.Point[] memory C_b,
        BigNum.instance[] memory F,
        BigNum.instance[] memory Z_b)
    internal view returns (bool check) {
        // Declare the left and right side of the check
        alt_bn128.Point memory left;
        alt_bn128.Point memory right;

        check = true;
        for (uint256 i = 0; i < n; i++) {
            left = alt_bn128.mul(BigNum.sub(x, F[i]), C_l[i]);
            left = alt_bn128.add(left, C_b[i]);
            //alt_bn128.Point memory right = alt_bn128.commit(0, proof.Z_b[i]);
            right = alt_bn128.mul(Z_b[i], alt_bn128.H());
            check = check && alt_bn128.isEqual(left, right);
        }
    }

    // Check the commitment to 0
    function verifyProofCheck3(
        uint256 n,
        BigNum.instance memory x,
        alt_bn128.Point[] memory commitments,
        Proof memory proof)
    internal view returns (bool check) {
        // Declare the left and right side of the check
        alt_bn128.Point memory left;
        alt_bn128.Point memory right;
        
        // N = 2**n
        uint256 N = commitments.length;

        alt_bn128.Point memory leftSum = alt_bn128.pointAtInf();
        BigNum.instance memory product;
        for (uint256 i = 0; i < N; i++) {
            // Calculate the product of F_j, i_j
            product = BigNum._new(1);
            for (uint256 j = 0; j < n; j++) {
                uint256 i_j = (i >> j) & 1;
                if (i_j == 1)
                    product = BigNum.mul(product, proof.F[j]);
                else
                    product = BigNum.mul(product, BigNum.sub(x, proof.F[j]));
            }
            leftSum = alt_bn128.add(leftSum, alt_bn128.mul(product, commitments[i]));
        }

        // Calculate the sum of the other commitments
        alt_bn128.Point memory rightSum = alt_bn128.pointAtInf();
        BigNum.instance memory xPowk = BigNum._new(1);
        for (uint256 k = 0; k < n; k++) {
            xPowk.neg = true;
            rightSum = alt_bn128.add(rightSum, alt_bn128.mul(xPowk, proof.C_d[k]));
            xPowk.neg = false;
            xPowk = BigNum.mul(xPowk, x);
        }

        left = alt_bn128.add(leftSum, rightSum);
        // alt_bn128.Point memory right = alt_bn128.commit(0, proof.z_d);
        right = alt_bn128.mul(proof.z_d, alt_bn128.H());
        check = alt_bn128.isEqual(left, right);
    }

    function hashAll(
        uint256 serialNumber,
        bytes memory message,
        alt_bn128.Point[] memory commitments,
        Proof memory proof)
    internal pure returns (bytes32 result) {
        // Hash the serial number
        result = sha256(abi.encodePacked(serialNumber));

        // Hash the message
        result = sha256(abi.encodePacked(result, message));

        // Hash the alt_bn128 curve generator points
        result = sha256(abi.encodePacked(result, alt_bn128.G().x, alt_bn128.G().y));
        result = sha256(abi.encodePacked(result, alt_bn128.H().x, alt_bn128.H().y));

        // Hash the commitments
        for (uint256 i = 0; i < commitments.length; i++)
            result = sha256(abi.encodePacked(result, commitments[i].x, commitments[i].y));
        for (uint256 i = 0; i < proof.C_l.length; i++)
            result = sha256(abi.encodePacked(result, proof.C_l[i].x, proof.C_l[i].y));
        for (uint256 i = 0; i < proof.C_a.length; i++)
            result = sha256(abi.encodePacked(result, proof.C_a[i].x, proof.C_a[i].y));
        for (uint256 i = 0; i < proof.C_b.length; i++)
            result = sha256(abi.encodePacked(result, proof.C_b[i].x, proof.C_b[i].y));
        for (uint256 i = 0; i < proof.C_d.length; i++)
            result = sha256(abi.encodePacked(result, proof.C_d[i].x, proof.C_d[i].y));
    }

    function verify(
        uint256 serialNumber,
        alt_bn128.Point[] memory commitments,
        uint256 n,
        Proof memory proof)
    internal view returns (bool result) {
        // Compute the hash used for the challenge
        uint256 xInt = uint256(hashAll(serialNumber, "Adrian", commitments, proof));
        BigNum.instance memory x = BigNum.instance(new uint128[](2), false);
        x.val[0] = uint128(xInt & BigNum.LOWER_MASK);
        x.val[1] = uint128(xInt >> 128);

        result = verifyProofCheck1(n, x, proof.C_l, proof.C_a, proof.F, proof.Z_a);
        result = result && verifyProofCheck2(n, x, proof.C_l, proof.C_b, proof.F, proof.Z_b);
        // result = result && verifyProofCheck3(n, x, commitments, proof);
    }

}
