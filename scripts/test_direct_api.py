# Path: /astoria_rag_hub/scripts/test_direct_api.py
# Filename: test_direct_api.py

import os
import json
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_direct_api_test():
    """Tries to insert a row using a direct HTTPS request."""
    logging.info("--- Testing Direct API Call (requests) ---")
    try:
        load_dotenv()
        
        # Get credentials from .env file
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY missing from .env")

        # --- Manually construct the API request ---
        # We are targeting the simple_test table
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # The URL for the REST API on the 'simple_test' table
        api_url = f"{url}/rest/v1/simple_test"
        
        # The simple data to send
        payload = {
            "content": "A direct API test using the requests library."
        }

        logging.info(f"Sending POST request to: {api_url}")
        
        # Make the web request
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))

        # Check the result
        if response.status_code == 201:
            logging.info(f"API Response (Status {response.status_code}): {response.json()}")
            logging.info("✅ SUCCESS: Direct API write was successful!")
        else:
            logging.error(f"❌ FAILED: Direct API write failed.")
            logging.error(f"Status Code: {response.status_code}")
            logging.error(f"Response Body: {response.text}")

    except Exception as e:
        logging.error(f"❌ FAILED with exception: {e}", exc_info=True)

if __name__ == "__main__":
    run_direct_api_test()
	# --- end-of-script test_direct_api.py ---
