// contracts/DeltaToken.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/access/AccessControlEnumerable.sol";
import "@openzeppelin/contracts/utils/Context.sol";

contract DeltaToken is Context, AccessControlEnumerable, ERC20Burnable, ERC20Pausable {
    bytes32 public constant MINTER_ROLE = keccak256("minterRole");
    bytes32 public constant PAUSER_ROLE = keccak256("pauserRole");

    uint256 public constant INITIAL_SUPPLY = 1000000000;


    constructor(uint256 initialSupply) ERC20("Delta", "DLT") {
        _mint(_msgSender(), initialSupply);
        _setupRole(DEFAULT_ADMIN_ROLE, _msgSender());

        _setupRole(MINTER_ROLE, _msgSender());
        _setupRole(PAUSER_ROLE, _msgSender());
    }

    function mint(address to, uint256 amount) public virtual {
        require(hasRole(MINTER_ROLE, _msgSender()), "Only minters can mint tokens");
        _mint(to, amount);
    }

    function pause() public virtual {
        require(hasRole(PAUSER_ROLE, _msgSender()), "Only pausers can pause the token");
        _pause();
    }

    function unpause() public virtual {
        require(hasRole(PAUSER_ROLE, _msgSender()), "Only pausers can unpause the token");
        _unpause();
    }

    // Not sure what this is for
    function _beforeTokenTransfer(address from, address to, uint256 value) internal virtual override(ERC20, ERC20Pausable) {
        super._beforeTokenTransfer(from, to, value);
    }

}