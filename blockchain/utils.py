from decouple import config
import json
from pathlib import Path
from web3 import Web3
from django.http import JsonResponse

# 🔹 Percorso ai file
WSL_PROJECT_PATH = config('WSL_PROJECT_PATH')
JSON_PATH = Path(WSL_PROJECT_PATH) / 'scripts' / 'address.json'
ABI_PATH = Path(WSL_PROJECT_PATH) / 'artifacts' / 'contracts' / 'AccessLog.sol' / 'AccessLog.json'

# Configura la connessione alla blockchain (Hardhat)
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Carica l'ABI
with open(ABI_PATH) as f:
    contract_abi = json.load(f)["abi"]

def get_contract_address():
    try:
        with open(JSON_PATH, 'r') as json_file:
            data = json.load(json_file)
            return data.get('contract_address', 'indirizzo_non_trovato')
    except FileNotFoundError:
        raise RuntimeError(f"Il file JSON non è stato trovato nel percorso: {JSON_PATH}")
    except json.JSONDecodeError:
        raise RuntimeError("Errore nella lettura del file JSON: Formato non valido.")

# 🔹 Instanzia il contratto
accessLog = web3.eth.contract(address=get_contract_address(), abi=contract_abi)

def log_access_on_blockchain(access_code, username):
    """Registra un accesso sulla blockchain"""
    try:
        account = web3.eth.accounts[0]  # Usa il primo account di Hardhat
        tx_hash = accessLog.functions.logAccess(username, access_code).transact({'from': account})
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        return {"status": "success", "tx_hash": receipt.transactionHash.hex()}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def get_access_logs():
    """Recupera tutti i log di accesso dalla blockchain e associa i nomi utente."""
    try:
        logs = accessLog.functions.getAccessLog().call()
        access_logs = []

        for log in logs:
            username = log[0]  # Nome utente salvato sulla blockchain
            timestamp = log[1]  # Timestamp dell'accesso
            hashed_code = log[2]  # Hash del codice

            access_logs.append({
                "username": username,
                "timestamp": timestamp,
                "hashed_code": hashed_code.hex()
            })

        return access_logs

    except Exception as e:
        print(f"❌ ERRORE in get_access_logs: {e}")  # Debug errore
        return JsonResponse({'error': str(e)}, status=500)
