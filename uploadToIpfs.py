# Import required libraries
import os
import typing as tp
import requests
import sys

# Custom tpe hints
ResponsePayload = tp.Dict[str, tp.Any]
OptionsDict = tp.Dict[str, tp.Any]
Headers = tp.Dict[str, str]

# global constants
API_ENDPOINT = "https://api.pinata.cloud/"


# def get_all_files(directory: str) -> tp.List[str]:
#     """get a list of absolute paths to every file located in the directory"""
#     paths: tp.List[str] = []
#     for root, dirs, files_ in os.walk(os.path.abspath(directory)):
#         for file in files_:
#             paths.append(os.path.join(root, file))
#     return paths


# def upload_directory_to_pinata(directory):

#     all_files: tp.List[str] = get_all_files(directory)
#     files = [("file", (file, open(file, "rb"))) for file in all_files]

#     print(files)

#     headers = {
#         "pinata_api_key": os.getenv("PINATA_API_KEY"),
#         "pinata_secret_api_key": os.getenv("PINATA_API_SECRET"),
#     }

#     response = requests.Response = requests.post(
#         url=PINATA_BASE_URL + endpoint, files=files, headers=headers
#     )

#     data = response.json()
#     print(data)
#     imageLinkBase = "ipfs://" + data["IpfsHash"] + "/"
#     return imageLinkBase


def pin_file_to_ipfs(path_to_file, options=None):
    """
    Pin any file, or directory, to Pinata's IPFS nodes
    More: https://docs.pinata.cloud/api-pinning/pin-file
    """
    url = API_ENDPOINT + "pinning/pinFileToIPFS"
    # headers = {k: self._auth_headers[k] for k in [
    #     pinataKeys.PINATA_API_KEY, pinataKeys.PINATA_SECRET_KEY]}

    headers = {
        "pinata_api_key": "2a7d204839bcc301e49e",
        "pinata_secret_api_key": "23a6ca2ccddd40128c704b0e5d8c327463709e2769eedc60c984f11e36c8d989",
    }

    files = tp.List[tp.Any]

    if os.path.isdir(path_to_file):
        all_files = get_all_files(path_to_file)
        files = [("file", (file, open(file, "rb"))) for file in all_files]
    else:
        files = [("file", open(path_to_file, "rb"))]

    if options is not None:
        if "pinataMetadata" in options:
            headers["pinataMetadata"] = options["pinataMetadata"]
        if "pinataOptions" in options:
            headers["pinataOptions"] = options["pinataOptions"]
    response = requests.post(
        url=url, files=files, headers=headers)
    print(response.json())
    return response.json()


def get_all_files(directory):
    """get a list of absolute paths to every file located in the directory"""
    paths = []
    for root, dirs, files_ in os.walk(os.path.abspath(directory)):
        for file in files_:
            paths.append(os.path.join(root, file))
    return paths


if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2])
