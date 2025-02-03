from decouple import config
import json
from pathlib import Path
from web3 import Web3

WSL_PROJECT_PATH = config('WSL_PROJECT_PATH')

JSON_PATH = Path(WSL_PROJECT_PATH) / 'scripts' / 'address.json'

ABI_PATH = Path(WSL_PROJECT_PATH) / 'artifacts' / 'contracts' / 'AccessLog.sol' / 'AccessLog.json'

# Configura la connessione alla rete locale Hardhat
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
    
def log_access_on_blockchain(code, is_valid):
    account = web3.eth.accounts[0]  # Usa il primo account di Hardhat
    tx_hash = accessLog.functions.logAccess(code, is_valid).transact({'from': account})
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

accessLog = web3.eth.contract(address=get_contract_address(), abi=contract_abi)
