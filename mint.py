import os
import ast
import time
import typing as tp
import requests
import sys
from web3 import Web3
from eth_account.messages import encode_structured_data
from dotenv import load_dotenv

load_dotenv()

BASE_NAME = os.getenv('BASE_NAME')
FIREBASE_URL = os.getenv('FIREBASE_URL')
USER_EMAIL = os.getenv('USER_EMAIL')
USER_PASSWORD = os.getenv('USER_PASSWORD')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')
SYMBOL = os.getenv('SYMBOL')
NFT_TRAITS_URL = os.getenv('NFT_TRAITS_URL')
POX_CONTRACT_ADDRESS = os.getenv('POX_CONTRACT_ADDRESS')
FORWARDER_CONTRACT_ADDRESS = os.getenv('FORWARDER_CONTRACT_ADDRESS')
CREATOR_ACCOUNT_ADDRESS = os.getenv('CREATOR_ACCOUNT_ADDRESS')
GET_NONCE_URL = os.getenv('GET_NONCE_URL')
UPDATE_CONTRACT_METADATA_URL = os.getenv('UPDATE_CONTRACT_METADATA_URL')
MINT_MFT_URL = os.getenv('MINT_MFT_URL')
METADATA_IPFS_URL = os.getenv('METADATA_IPFS_URL')
CREATOR_PRIVATE_KEY = os.getenv('CREATOR_PRIVATE_KEY')
COLLECTION_SIZE = os.getenv('COLLECTION_SIZE')
COLLECTION_PRICE = os.getenv("COLLECTION_PRICE")
FIREBASE_ASSETURL = os.getenv("FIREBASE_ASSETURL")
FILEARRAY = os.getenv('FILEARRAY')

filearray = ast.literal_eval(FILEARRAY)


def main():
    # GET NONCE AND SIGNATURE FOR CREATOR ACCOUNT
    nonce, signature = get_nonce(
        CREATOR_ACCOUNT_ADDRESS, POX_CONTRACT_ADDRESS, FORWARDER_CONTRACT_ADDRESS)

    # UPDATE METADATA URI IN CONTRACT
    update_request_body = {
        "from": CREATOR_ACCOUNT_ADDRESS,
        "nonce": nonce,
        "signature": signature,
        "metadataUri": METADATA_IPFS_URL,
        'poxContractAddress': POX_CONTRACT_ADDRESS,
        'customForwarderContractAddress': FORWARDER_CONTRACT_ADDRESS
    }
    r = requests.patch(url=UPDATE_CONTRACT_METADATA_URL,
                       json=update_request_body)
    print(r.json())

    time.sleep(20)

    loops = 0
    minted = 0
    mintAmount = 0
    if int(COLLECTION_SIZE) > 50:  # minting in batches of 50
        loops = int(COLLECTION_SIZE)/50 + 1
        mintAmount = 50
    else:
        mintAmount = int(COLLECTION_SIZE)

    for k in range(int(loops)):
        nonce, signature = get_nonce(
            CREATOR_ACCOUNT_ADDRESS, POX_CONTRACT_ADDRESS, FORWARDER_CONTRACT_ADDRESS)
        time.sleep(20)
        if k == int(loops) - 1:
            mintAmount = int(COLLECTION_SIZE) - minted
        priceMap = get_price_map(
            (mintAmount + minted), COLLECTION_PRICE, minted)
        fileArray = get_file_array((mintAmount + minted), minted)
        mint_nft_request_body = {
            "name": BASE_NAME,
            "description": COLLECTION_NAME,
            "priceMap": priceMap,
            "fileArray": fileArray,
            "currency": "INR",
            # "totalQuantity": int(COLLECTION_SIZE),
            "totalQuantity": mintAmount,
            "mintMechanism": "BUY",
            "signature": signature,
            "nonce": nonce,
            "rarity": "UNIQUE",
            "type": {
                "value": "COLLECTIBLE",
                "title": BASE_NAME,
                "description": COLLECTION_NAME
            },
            "networkId": "6191fa723141b277ef5a9883",
            "collectionName": COLLECTION_NAME,
            "originalAssetUrl": FIREBASE_ASSETURL,
            "metadata": {
                "mediaType": "image"
            },
        }
        encodedjwt = get_firebase_token()
        request_headers = {"Authorization": "Bearer {}".format(encodedjwt)}
        time.sleep(10)
        r = requests.post(url=MINT_MFT_URL, headers=request_headers,
                          json=mint_nft_request_body)
        print(r.json())
        minted += mintAmount
        time.sleep(30)  # Sleep for 30 seconds


def get_nonce(creator_address, pox_address, forwarder_address):
    payload = {
        'account': creator_address,
        'poxContractAddress': pox_address,
        'customForwarderContractAddress': forwarder_address
    }
    r = requests.get(GET_NONCE_URL, params=payload)
    print(r)
    nonce = r.json()["data"]["nonce"]
    tosign = r.json()["data"]["toSign"]
    tosign["message"]["nonce"] = int(tosign["message"]["nonce"])
    print(tosign)
    encoded_data = encode_structured_data(tosign)
    w3 = Web3(Web3.IPCProvider())
    signature = w3.eth.account.sign_message(
        encoded_data, CREATOR_PRIVATE_KEY)
    print(nonce)
    print(signature)
    #tx_hash = w3.toHex(w3.keccak(signature.signature))
    required_signature = signature[4].hex()
    print(required_signature)
    return nonce, required_signature


def get_price_map(size, price, mintedIndex):
    priceMap = {}
    for i in range(mintedIndex, int(size)):
        priceMap[str(i)] = int(price)
    print(priceMap)
    return priceMap


def get_file_array(size, mintedIndex):
    filearr = []
    filearr = filearray[int(mintedIndex):(int(mintedIndex) + int(size))]
    print(filearr)
    return filearr


def get_firebase_token():
    auth_json = {
        "email": "",
        "password": "",
        "returnSecureToken": True
    }
    auth_json['email'] = USER_EMAIL
    auth_json['password'] = USER_PASSWORD
    firebase_response = requests.post(url=FIREBASE_URL, json=auth_json)
    print(firebase_response.json())
    encodedjwt = firebase_response.json()["idToken"]
    return encodedjwt


main()
