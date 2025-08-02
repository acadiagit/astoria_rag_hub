# Path: /astoria_rag_hub/scripts/test_connections.py
# Filename: test_connections.py

import os
import logging
from dotenv import load_dotenv
import psycopg2
from supabase.client import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_postgres():
    """Tests the connection to the PostgreSQL database."""
    logging.info("--- Testing PostgreSQL Connection ---")
    try:
        conn_string = "dbname='{db}' user='{user}' host='{host}' password='{pw}' port='{port}'".format(
            db=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            host=os.getenv('POSTGRES_HOST'),
            pw=os.getenv('POSTGRES_PASSWORD'),
            port=os.getenv('POSTGRES_PORT')
        )
        with psycopg2.connect(conn_string) as conn:
            logging.info("✅ PostgreSQL connection successful!")
        return True
    except Exception as e:
        logging.error(f"❌ PostgreSQL connection FAILED: {e}")
        return False

def test_supabase_client_init():
    """Tests the initialization of the Supabase client."""
    logging.info("--- Testing Supabase Client Initialization ---")
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY missing from .env")
        
        create_client(url, key)
        logging.info("✅ Supabase client initialized successfully!")
        return True
    except Exception as e:
        logging.error(f"❌ Supabase client initialization FAILED: {e}")
        return False

# --- ADDED THIS NEW FUNCTION TO TEST THE WRITE OPERATION ---
def test_supabase_write():
    """Tests writing a single row to the Supabase 'documents' table."""
    logging.info("--- Testing Supabase Write Operation ---")
    TABLE_NAME = "documents"
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        supabase: Client = create_client(url, key)

        test_data = {
            "content": "This is a connection write test.",
            # A fake embedding vector with the correct number of dimensions (384 for all-MiniLM-L6-v2)
            "embedding": [0.1] * 384 
        }

        response = supabase.from_(TABLE_NAME).insert(test_data).execute()

        if response.data:
            logging.info(f"API Response: {response.data}")
            logging.info("✅ Supabase write successful!")
            return True
        else:
            logging.error(f"❌ Supabase write FAILED: {response.error or 'No data returned'}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Supabase write FAILED with exception: {e}")
        return False

if __name__ == "__main__":
    print("Running connection tests...")
    load_dotenv()
    pg_ok = test_postgres()
    sb_init_ok = test_supabase_client_init()
    # --- ADDED THE CALL TO THE NEW WRITE TEST ---
    sb_write_ok = test_supabase_write()
    
    print("\n--- Test Summary ---")
    print(f"PostgreSQL Connection: {'SUCCESS' if pg_ok else 'FAILED'}")
    print(f"Supabase Client Init:  {'SUCCESS' if sb_init_ok else 'FAILED'}")
    print(f"Supabase Write Test:   {'SUCCESS' if sb_write_ok else 'FAILED'}")

#end-of-file
