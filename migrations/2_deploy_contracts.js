const FraudGuard = artifacts.require("FraudGuard");

module.exports = function (deployer) {
    deployer.deploy(FraudGuard);
};