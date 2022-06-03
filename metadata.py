#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import time
import os
from progressbar import progressbar
import json
from copy import deepcopy
import requests

import warnings
from dotenv import load_dotenv

load_dotenv()
warnings.simplefilter(action='ignore', category=FutureWarning)

BASE_IMAGE_URL = os.getenv('BASE_IMAGE_URL')
BASE_NAME = os.getenv('BASE_NAME')
OUTPUT_IMAGE_PATH = os.getenv('OUTPUT_IMAGE_PATH')
OUTPUT_METADATA_PATH = os.getenv('OUTPUT_METADATA_PATH')
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
COLLECTION_DESCRIPTION = os.getenv('COLLECTION_DESCRIPTION')

BASE_JSON = {
    "name": BASE_NAME,
    "description": COLLECTION_DESCRIPTION,
    "image": BASE_IMAGE_URL,
    "attributes": [],
}


# Get metadata and JSON files path based on edition
def generate_paths(edition_name=None):
    # edition_path = os.path.join('output', 'edition ' + str(edition_name))
    # metadata_path = os.path.join(edition_path, 'metadata.csv')
    # json_path = os.path.join(edition_path, 'json')
    # edition_path = os.path.join('output', 'edition ' + str(edition_name))
    edition_path = OUTPUT_IMAGE_PATH
    metadata_path = os.path.join(OUTPUT_IMAGE_PATH, 'metadata.csv')
    json_path = OUTPUT_METADATA_PATH

    return edition_path, metadata_path, json_path

# Function to convert snake case to sentence case


def clean_attributes(attr_name):

    clean_name = attr_name.replace('_', ' ')
    clean_name = list(clean_name)

    for idx, ltr in enumerate(clean_name):
        if (idx == 0) or (idx > 0 and clean_name[idx - 1] == ' '):
            clean_name[idx] = clean_name[idx].upper()

    clean_name = ''.join(clean_name)
    return clean_name


# Function to get attribure metadata
def get_attribute_metadata(metadata_path):

    # Read attribute data from metadata file
    df = pd.read_csv(metadata_path)
    df = df.drop('Unnamed: 0', axis=1)
    df.columns = [clean_attributes(col) for col in df.columns]

    # Get zfill count based on number of images generated
    # -1 according to nft.py. Otherwise not working for 100 NFTs, 1000 NTFs, 10000 NFTs and so on
    zfill_count = len(str(df.shape[0]-1))

    return df, zfill_count

# Main function that generates the JSON metadata


def main():

    # Get edition name
    print("Enter edition you want to generate metadata for: ")
    while True:
        # edition_name = input()
        # edition_path, metadata_path, json_path = generate_paths(edition_name)
        edition_path, metadata_path, json_path = generate_paths()

        if os.path.exists(edition_path):
            print("Edition exists! Generating JSON metadata...")
            break
        else:
            print("Oops! Looks like this edition doesn't exist! Check your output folder to see what editions exist.")
            print("Enter edition you want to generate metadata for: ")
            continue

    # Make json folder
    if not os.path.exists(json_path):
        os.makedirs(json_path)

    # Get attribute data and zfill count
    df, zfill_count = get_attribute_metadata(metadata_path)
    # print(df)
    metadata = []

    for idx, row in progressbar(df.iterrows()):

        # Get a copy of the base JSON (python dict)
        item_json = deepcopy(BASE_JSON)

        # Append number to base name
        item_json['name'] = item_json['name'] + str(idx)

        # Append image PNG file name to base image path
        item_json['image'] = item_json['image'] + \
            '/' + str(idx).zfill(zfill_count) + '.png'

        # Convert pandas series to dictionary
        attr_dict = dict(row)

        # Add all existing traits to attributes dictionary
        for attr in attr_dict:

            if attr_dict[attr] != 'none':
                item_json['attributes'].append(
                    {'trait_type': attr, 'value': attr_dict[attr]})

        # Write file to json folder
        item_json_path = os.path.join(json_path, str(idx))
        with open(item_json_path, 'w') as f:
            json.dump(item_json, f)
        item_json["tokenId"] = str(idx)
        metadata.append(item_json)

    item_json_path = os.path.join(json_path, "metadata")
    with open(item_json_path, 'w') as f:
        json.dump(metadata, f)

    # store nft traits data in mongodb
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
    request_headers = {"Authorization": "Bearer {}".format(encodedjwt)}

    request_body = {"collectionName": COLLECTION_NAME,
                    "symbol": SYMBOL, "metadata": metadata}
    response = requests.post(
        url=NFT_TRAITS_URL, headers=request_headers, json=request_body)
    print(response)
    # print(metadata)


# Run the main function
main()
