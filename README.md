ChainML Guard: Proactive Ethereum Fraud Detection
ChainML Guard is a sophisticated security solution that combines Deep Learning and Blockchain technology to predict and block frauds, such as wallet drainers, before a transaction is signed.

Developed by: REHOUNI Ouiame and ANINI Hiba

Project Architecture
The application is structured into three distinct layers:

AI Engine: A Multi-Layer Perceptron (MLP) model developed with TensorFlow to analyze transactional behavior.

Blockchain Layer: A Solidity Smart Contract (Truffle) designed for secure fund transfers.

Frontend/Backend: A Flask-based interface providing seamless interaction with MetaMask.

Installation and Deployment (Docker)
The project is fully containerized. No local installation of Python or AI libraries is required on your host machine.

1. Prerequisites
Docker Desktop installed and running.

Ganache for local blockchain simulation.

MetaMask configured on the Ganache network (RPC: http://127.0.0.1:7545).

2. Clone the Repository
Bash
git clone https://github.com/ouiamerehouni-lang/ChainML-Guard.git
cd ChainML-Guard
3. Launch the Application with Docker
Run the following two commands in your terminal:

Build the image:

Bash
docker build -t chainml-guard .
Run the container:

Bash
docker run -p 5000:5000 chainml-guard
4. Access the Interface
Open your web browser and navigate to the following address: http://localhost:5000
