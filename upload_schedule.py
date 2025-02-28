import os
import json
import requests
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

BLOB_READ_WRITE_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN")
BLOB_STORE_ID = os.getenv("BLOB_STORE_ID")

if not BLOB_READ_WRITE_TOKEN or not BLOB_STORE_ID:
    logger.error("Missing environment variables. Please check .env file.")
    exit(1)

logger.info(f"BLOB_STORE_ID: {BLOB_STORE_ID}")
logger.info(f"BLOB_READ_WRITE_TOKEN set: {bool(BLOB_READ_WRITE_TOKEN)}")

# Load schedule data
try:
    with open('schedule.json', 'r', encoding='utf-8') as f:
        schedule_data = json.load(f)
        logger.info("Schedule data loaded successfully")
except Exception as e:
    logger.error(f"Failed to load schedule.json: {str(e)}")
    exit(1)

# Convert data to JSON string and encode to bytes
json_data = json.dumps(schedule_data).encode()

# Create request headers
headers = {
    "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}"
}

# Try to create the store if it doesn't exist
try:
    logger.info("Checking if store exists")
    store_check = requests.get(
        f"https://blob.vercel-storage.com/list?storeId={BLOB_STORE_ID}",
        headers=headers,
        timeout=10
    )
    
    if store_check.status_code == 404:
        logger.info("Store doesn't exist, creating it")
        create_store = requests.put(
            "https://blob.vercel-storage.com/store",
            headers=headers,
            json={
                "id": BLOB_STORE_ID
            },
            timeout=10
        )
        
        if create_store.status_code not in [200, 201, 409]:
            logger.error(f"Failed to create store: {create_store.status_code} - {create_store.text}")
            exit(1)
        else:
            logger.info("Store created or already exists")
except Exception as e:
    logger.error(f"Error checking store: {str(e)}")
    exit(1)

try:
    # Get a presigned URL
    logger.info("Getting presigned URL for upload")
    presigned_url_response = requests.post(
        "https://blob.vercel-storage.com/post-url",
        headers=headers,
        json={
            "size": len(json_data),
            "contentType": "application/json",
            "storeId": BLOB_STORE_ID,
            "pathname": "schedule.json",
            "access": "public",
            "addRandomSuffix": False
        },
        timeout=10
    )
    
    if presigned_url_response.status_code != 200:
        logger.error(f"Failed to get presigned URL: {presigned_url_response.status_code} - {presigned_url_response.text}")
        exit(1)
    
    presigned_data = presigned_url_response.json()
    
    if "url" not in presigned_data:
        logger.error(f"URL not found in presigned data: {presigned_data}")
        exit(1)
    
    # Upload the file to the presigned URL
    logger.info(f"Uploading file to presigned URL")
    upload_response = requests.put(
        presigned_data["url"],
        data=json_data,
        headers={
            "Content-Type": "application/json"
        },
        timeout=10
    )
    
    if upload_response.status_code != 200:
        logger.error(f"Failed to upload file: {upload_response.status_code} - {upload_response.text}")
        exit(1)
    
    logger.info("Schedule successfully uploaded to Vercel Blob Storage")
    
    # Print the public URL
    public_url = f"https://{BLOB_STORE_ID}.public.blob.vercel-storage.com/schedule.json"
    logger.info(f"Public URL: {public_url}")
    
except Exception as e:
    logger.error(f"Error during upload: {str(e)}")
    exit(1) 