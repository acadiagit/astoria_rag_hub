# Path: /astoria_rag_hub/scripts/ingest_data.py
# Filename: ingest_data.py

import os
import sys
import logging
import math
import time # Import the time module for sleeping
from dotenv import load_dotenv
from httpx import ReadError # Import the specific error

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.rag_components.data_loader import load_documents_from_directory
from app.rag_components.vector_store import get_vector_store

# Configure logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to run the data ingestion pipeline.
    """
    logging.info("Starting data ingestion pipeline...")
    load_dotenv()
    
    # 1. Load documents
    documents = load_documents_from_directory('data/maritime_history')
    if not documents:
        logging.warning("No documents found in the directory. Exiting pipeline.")
        return
        
    # 2. Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    logging.info(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    
    # 3. Initialize vector store
    logging.info("Initializing vector store...")
    vector_store = get_vector_store()

    # --- UPDATED BATCHING AND RETRY LOGIC ---
    batch_size = 10  # --- REDUCED BATCH SIZE ---
    max_retries = 3
    retry_delay = 5  # seconds

    total_chunks = len(chunks)
    num_batches = math.ceil(total_chunks / batch_size)

    logging.info(f"Preparing to upload {total_chunks} chunks in {num_batches} batches of {batch_size}.")

    for i in range(0, total_chunks, batch_size):
        batch_num = (i // batch_size) + 1
        batch = chunks[i:i + batch_size]
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Uploading batch {batch_num}/{num_batches}...")
                vector_store.add_documents(batch)
                logging.info(f"Batch {batch_num} uploaded successfully.")
                break  # Exit the retry loop on success
            except ReadError as e:
                logging.warning(f"Batch {batch_num} failed on attempt {attempt + 1}/{max_retries} due to network error. Retrying in {retry_delay} seconds...")
                if attempt + 1 == max_retries:
                    logging.error(f"Batch {batch_num} failed after {max_retries} attempts. Stopping script. Error: {e}")
                    return # Stop the entire script if a batch fails completely
                time.sleep(retry_delay)
    # --- END OF UPDATED LOGIC ---
    
    logging.info("✅ Data ingestion pipeline completed successfully!")

if __name__ == "__main__":
    main()

#end-of-file
