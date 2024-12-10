import json
from web3 import Web3

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

with open('blockchain/abi/Lock.json') as f:
    contract_abi = json.load(f)["abi"]

contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def get_message():
    """Recupera il messaggio salvato nel contratto."""
    return contract.functions.message().call()
