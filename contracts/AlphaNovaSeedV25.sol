// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AlphaNovaSeedV25 is ERC721, Ownable {
    uint256 public nextTokenId = 1;
    mapping(uint256 => string) private _uris;
    address public registry;

    event RegistrySet(address indexed registry);

    modifier onlyRegistry() {
        require(msg.sender == registry, "NOT_REGISTRY");
        _;
    }

    constructor(address initialOwner) ERC721("Alpha Nova-Seed", "ANSEED") Ownable(initialOwner) {}

    function setRegistry(address _registry) external onlyOwner {
        require(_registry != address(0), "BAD_REGISTRY");
        registry = _registry;
        emit RegistrySet(_registry);
    }

    function mint(address to, string calldata uri) external onlyRegistry returns (uint256 tokenId) {
        tokenId = nextTokenId++;
        _safeMint(to, tokenId);
        _uris[tokenId] = uri;
    }

    function setTokenURI(uint256 tokenId, string calldata uri) external onlyRegistry {
        require(_ownerOf(tokenId) != address(0), "NO_TOKEN");
        _uris[tokenId] = uri;
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "NO_TOKEN");
        return _uris[tokenId];
    }
}
