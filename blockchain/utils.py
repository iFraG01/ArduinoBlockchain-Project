from decouple import config
import json
from pathlib import Path
from web3 import Web3
from django.http import JsonResponse

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib

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

# Crittografia AES256
def encrypt_code_aes256(access_code: str) -> str:
    """Cripta il codice di accesso usando AES256 in modalità CBC"""
    
    key = b64decode(config("AES_SECRET_KEY"))
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(access_code.encode(), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    encrypted = iv + ciphertext
    return encrypted.hex()

def decrypt_code_aes256(encrypted_hex: str) -> str:
    """Decifra un codice criptato in esadecimale con AES256 CBC"""

    key = b64decode(config("AES_SECRET_KEY"))
    encrypted_bytes = bytes.fromhex(encrypted_hex)
    iv = encrypted_bytes[:16]
    ciphertext = encrypted_bytes[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(ciphertext)
    decrypted = unpad(decrypted_padded, AES.block_size)
    return decrypted.decode()

# Log su blockchain
def log_access_on_blockchain(username, access_code, result):
    """Registra un accesso sulla blockchain"""

    try:
        account = web3.eth.accounts[0]
        encrypted_code = encrypt_code_aes256(access_code)
        tx_hash = accessLog.functions.logAccess(username, bytes.fromhex(encrypted_code), result).transact({'from': account})
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        return {"status": "success", "tx_hash": receipt.transactionHash.hex()}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_access_logs():
    """Recupera tutti i log di accesso dalla blockchain"""
    try:
        logs = accessLog.functions.getAccessLog().call()
        access_logs = []
        for log in logs:
            username = log[0]
            timestamp = log[1]
            hashed_code = log[2]
            result = log[3]
            access_logs.append({
                "username": username,
                "timestamp": timestamp,
                "hashed_code": hashed_code.hex(),
                "result": result
            })
        return access_logs
    except Exception as e:
        print(f"❌ ERRORE in get_access_logs: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def log_user_operation(operation_type, username):
    """Registra un'operazione sugli utenti sulla blockchain"""
    try:
        account = web3.eth.accounts[0]
        tx_hash = accessLog.functions.logUserOperation(operation_type, username).transact({'from': account})
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return {"status": "success", "tx_hash": receipt.transactionHash.hex()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_user_operations():
    """Recupera tutti i log delle operazioni utenti dalla blockchain"""
    try:
        operations = accessLog.functions.getUserOperations().call()
        user_operations = []
        for operation in operations:
            operation_type = operation[0]
            username = operation[1]
            timestamp = operation[2]
            user_operations.append({
                "operationType": operation_type,
                "userName": username,
                "timestamp": timestamp
            })
        return user_operations
    except Exception as e:
        print(f"❌ ERRORE in get_user_operations: {e}")
        return []
