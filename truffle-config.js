module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 7545,            // Port standard de Ganache GUI (vérifie sur Ganache)
      network_id: "*",       // Match n'importe quel ID de réseau
    },
  },

  mocha: {
    // timeout: 100000
  },

  compilers: {
    solc: {
      version: "0.8.0",      // Version exacte de ton contrat
      settings: {
        optimizer: {
          enabled: true,
          runs: 200
        }
      }
    }
  },
};