// contracts/SigmaProofVerifier.sol
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./BigNum.sol";


library SigmaProofVerifier {

    uint256 constant G = 3007057779649931580237598654612510797095951971612630025891176454468165002055;
    uint256 constant H = 20354936247998155748817459761265066334754915076915271771709029462851510023744;

    struct Proof {
        uint256[] C_l;
        uint256[] C_a;
        uint256[] C_b;
        uint256[] C_d;
        BigNum.instance[] F;
        BigNum.instance[] Z_a;
        BigNum.instance[] Z_b;
        BigNum.instance z_d;
    }

    function commit(BigNum.instance memory m, BigNum.instance memory r) internal view returns (uint256) {
        return mulmod(BigNum.modExp(G, m), BigNum.modExp(H, r), BigNum.PRIME);
    }

    // Check the commitments to l part 1
    function verifyProofCheck1(
        uint256 n,
        BigNum.instance memory x,
        uint256[] memory C_l, 
        uint256[] memory C_a,
        BigNum.instance[] memory F,
        BigNum.instance[] memory Z_a)
    internal view returns (bool check) {
        // Declare the left and right side of the check
        uint256 left;
        uint256 right;

        // Check the commitments to l
        check = true;
        for (uint256 i = 0; i < n; i++) {
            left = BigNum.modExp(C_l[i], x);
            left = mulmod(left, C_a[i], BigNum.PRIME);
            right = commit(F[i], Z_a[i]);
            check = check && left == right;
        }
    }

    // Check the commitments to l part 2
    function verifyProofCheck2(
        uint256 n,
        BigNum.instance memory x,
        uint256[] memory C_l, 
        uint256[] memory C_b,
        BigNum.instance[] memory F,
        BigNum.instance[] memory Z_b)
    internal view returns (bool check) {
        // Declare the left and right side of the check
        uint256 left;
        uint256 right;

        check = true;
        for (uint256 i = 0; i < n; i++) {
            left = BigNum.modExp(C_l[i], BigNum.sub(x, F[i]));
            left = mulmod(left, C_b[i], BigNum.PRIME);
            //ECC.Point memory right = ECC.commit(0, proof.Z_b[i]);
            right = BigNum.modExp(H, Z_b[i]);
            check = check && left == right;
        }
    }

    // Check the commitment to 0
    function verifyProofCheck3(
        uint256 n,
        BigNum.instance memory x,
        uint256[] memory commitments,
        Proof memory proof)
    internal view returns (bool check) {
        // Declare the left and right side of the check
        uint256 left;
        uint256 right;
        
        // N = 2**n
        uint256 N = commitments.length;

        uint256 leftProduct = 1;
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
            leftProduct = mulmod(leftProduct, BigNum.modExp(commitments[i], product), BigNum.PRIME);
        }

        // Calculate the sum of the other commitments
        uint256 rightProduct = 1;
        BigNum.instance memory xPowk = BigNum._new(1);
        for (uint256 k = 0; k < n; k++) {
            xPowk.neg = true;
            rightProduct = mulmod(rightProduct, BigNum.modExp(proof.C_d[k], xPowk), BigNum.PRIME);
            xPowk.neg = false;
            xPowk = BigNum.mul(xPowk, x);
        }

        left = mulmod(leftProduct, rightProduct, BigNum.PRIME);
        // ECC.Point memory right = ECC.commit(0, proof.z_d);
        right = BigNum.modExp(H, proof.z_d);
        check = left == right;
    }

    function hashAll(
        uint256 serialNumber,
        bytes memory message,
        uint256[] memory commitments,
        Proof memory proof)
    internal pure returns (bytes32 result) {
        // Hash the serial number
        result = sha256(abi.encodePacked(serialNumber));

        // Hash the message
        result = sha256(abi.encodePacked(result, message));

        // Hash the ECC curve generator points
        result = sha256(abi.encodePacked(result, G));
        result = sha256(abi.encodePacked(result, H));

        // Hash the commitments
        for (uint256 i = 0; i < commitments.length; i++)
            result = sha256(abi.encodePacked(result, commitments[i]));
        for (uint256 i = 0; i < proof.C_l.length; i++)
            result = sha256(abi.encodePacked(result, proof.C_l[i]));
        for (uint256 i = 0; i < proof.C_a.length; i++)
            result = sha256(abi.encodePacked(result, proof.C_a[i]));
        for (uint256 i = 0; i < proof.C_b.length; i++)
            result = sha256(abi.encodePacked(result, proof.C_b[i]));
        for (uint256 i = 0; i < proof.C_d.length; i++)
            result = sha256(abi.encodePacked(result, proof.C_d[i]));
    }

    function verify(
        uint256 serialNumber,
        uint256[] memory commitments,
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
        result = result && verifyProofCheck3(n, x, commitments, proof);
    }
}
