from flask import Flask, request, jsonify
from web3 import Web3
import json
import base64
import hashlib
from flask_cors import CORS
from fingerprint_scanner import scan_fingerprint  # Replace with actual biometric scanner library
#Due to insufficeant data the biometric verification will allways give the verification faild 

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend interaction

# Connect to Ethereum Blockchain (Use Infura or Local Ganache for testing)
blockchain_url = "http://127.0.0.1:7545"  # Change to Infura or mainnet later
web3 = Web3(Web3.HTTPProvider(blockchain_url))

# Smart contract details (Replace with actual deployed contract address & ABI)
contract_address = "0xYourContractAddress"

# Replace with the actual ABI from your compiled Solidity smart contract
contract_abi = [
    {
        "constant": True,
        "inputs": [{"name": "voterId", "type": "string"}],
        "name": "getBiometricHash",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# Load contract
try:
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    print("🔗 Connected to blockchain successfully!")
except Exception as e:
    contract = None
    print(f"❌ Blockchain connection error: {str(e)}")

@app.route("/start-auth", methods=["POST"])
def start_auth():
    data = request.json
    voter_id = data.get("voter_id")

    if not voter_id:
        return jsonify({"status": "error", "message": "Voter ID is required"}), 400

    # Simulated WebAuthn challenge (For real-world use, integrate WebAuthn API)
    challenge = base64.b64encode(b"random_challenge").decode()

    return jsonify({"status": "success", "challenge": challenge})

@app.route("/verify", methods=["POST"])
def verify_voter():
    data = request.json
    voter_id = data.get("voter_id")

    if not voter_id:
        return jsonify({"status": "error", "message": "Voter ID is required"}), 400

    if contract is None:
        return jsonify({"status": "error", "message": "Blockchain connection failed"}), 500

    try:
        # Fetch the stored biometric hash from the blockchain
        stored_hash = contract.functions.getBiometricHash(voter_id).call()

        # Scan fingerprint using real biometric hardware (returns raw fingerprint data)
        fingerprint_data = scan_fingerprint()

        if fingerprint_data is None:
            return jsonify({"status": "error", "message": "Fingerprint scan failed"}), 400

        # Hash the scanned fingerprint data
        scanned_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()

        # Compare hashes
        if scanned_hash == stored_hash:
            return jsonify({"status": "success", "message": "Voter verified successfully"})
        else:
            return jsonify({"status": "error", "message": "Biometric verification failed"}), 401

    except Exception as e:
        return jsonify({"status": "error", "message": f"Internal error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
