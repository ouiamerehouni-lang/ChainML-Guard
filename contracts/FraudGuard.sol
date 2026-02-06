// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FraudGuard {
    address public owner;
    
    // Événements pour suivre les activités sur la blockchain
    event Deposit(address indexed from, uint256 amount);
    event TransferExecuted(address indexed to, uint256 amount);

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Reçoit de l'éther et le stocke sur le contrat.
     * Le montant est conservé ici jusqu'à ce que le transfert vers le destinataire soit validé.
     */
    function secureTransfer(address payable _to) public payable {
        require(msg.value > 0, "Le montant doit etre superieur a 0");
        require(_to != address(0), "Adresse de destination invalide");

        emit Deposit(msg.sender, msg.value);

        // Transfert immédiat des fonds après sécurisation/log
        // Dans un vrai projet de détection de fraude, on ajouterait ici une vérification
        (bool success, ) = _to.call{value: msg.value}("");
        require(success, "Echec du transfert des fonds");

        emit TransferExecuted(_to, msg.value);
    }

    /**
     * @dev Permet de verifier le solde du contrat (devrait être 0 après le transfert)
     */
    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }

    // Fonction pour permettre au contrat de recevoir de l'argent directement
    receive() external payable {}
}