// contracts/SigmaProofVerifier.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./P256.sol";


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
        BigNum.instance memory x,
        ECC.Point[] memory commitments,
        SigmaProof memory proof)
    internal pure returns (bool check) {
        // Declare the left and right side of the check
        ECC.Point memory left;
        ECC.Point memory right;
        
        uint256 N = 2**n;
        //uint256 N = 4;

        ECC.Point memory leftSum = ECC.pointAtInf();
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
            leftSum = ECC.add(leftSum, ECC.mul(product, commitments[i]));
        }

        // Calculate the sum of the other commitments
        ECC.Point memory rightSum = ECC.pointAtInf();
        BigNum.instance memory xPowk = BigNum._new(1);
        for (uint256 k = 0; k < n; k++) {
            xPowk.neg = true;
            rightSum = ECC.add(rightSum, ECC.mul(xPowk, proof.C_d[k]));
            xPowk.neg = false;
            xPowk = BigNum.mul(xPowk, x);
        }

        left = ECC.add(leftSum, rightSum);
        // ECC.Point memory right = ECC.commit(0, proof.z_d);
        right = ECC.mul(proof.z_d, ECC.H());
        check = ECC.isEqual(left, right);
    }

    function verify(ECC.Point[] memory commitments, SigmaProof memory proof) public pure returns (bool check1, bool check2, bool check3) {
        
        // For now, hardcode the length of the commitment list
        uint256 n = 2;

        // For now, hardcode the challenge
        BigNum.instance memory x = BigNum._new(123456789);

        check1 = verifyProofCheck1(n, x, proof.C_l, proof.C_a, proof.F, proof.Z_a);
        check2 = verifyProofCheck2(n, x, proof.C_l, proof.C_b, proof.F, proof.Z_b);
        check3 = verifyProofCheck3(n, x, commitments, proof);
    }

    function hashAll(uint256 serialNumber, bytes memory message,  ECC.Point[] memory commitments, SigmaProof memory proof) public pure returns (bytes32 result) {
        // Hash the serial number
        result = sha256(abi.encodePacked(serialNumber));

        // Hash the message
        result = sha256(abi.encodePacked(result, message));

        // Hash the ECC curve generator points
        result = sha256(abi.encodePacked(result, ECC.G().x, ECC.G().y));
        result = sha256(abi.encodePacked(result, ECC.H().x, ECC.H().y));

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

    function testHash(ECC.Point[] memory points, BigNum.instance[] memory nums) public pure returns (bytes32 result) {
        // hash all the points
        result = 0x00;
        for (uint256 i = 0; i < points.length; i++)
            result = sha256(abi.encodePacked(result, points[i].x, points[i].y));

        // hash all the numbers
        for (uint256 i = 0; i < nums.length; i++) {
            // hash all the cells individually
            for (uint256 j = 0; j < nums[i].val.length; j++)
                // nums[i].val[j] is a uint128 not a uint256 --> encide as bytes16
                result = sha256(abi.encodePacked(result, nums[i].val[j]));
            // nums[i].neg is a bool not a uint256 --> encode as bytes1
            result = sha256(abi.encodePacked(result, nums[i].neg));
        }
    }
}
