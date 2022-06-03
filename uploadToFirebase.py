from firebase_admin import credentials, initialize_app, storage
import os
from dotenv import load_dotenv

load_dotenv()

OUTPUT_IMAGE_PATH = os.getenv('OUTPUT_IMAGE_PATH')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
STORAGE_BUCKET = os.getenv("STORAGE_BUCKET")

# Init firebase with your credentials
cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
initialize_app(cred, {'storageBucket': STORAGE_BUCKET})
# Put your local file path
path = OUTPUT_IMAGE_PATH
assetUrl = "https://storage.googleapis.com/" + \
    str(STORAGE_BUCKET)  + str(path) + "/"
print("Replace the below url in .env under FIREBASE_ASSETURL:")
print(assetUrl)
print("")
fileArray = []
for filename in os.listdir(path):
    if filename.endswith(".png"):
        # print(filename)
        x = filename.split(".")
        fileArray.append(x[0])
        bucket = storage.bucket()
        file = path + "/" + str(filename)
        blob = bucket.blob(file)
        blob.upload_from_filename(file)
        # Opt : if you want to make public access from the URL
        blob.make_public()
        # print("file url:", blob.public_url)
fileArray.sort(key=int)
print("Replace the below array in .env under FILEARRAY:")
print(fileArray)
