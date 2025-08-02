# Path: /astoria_rag_hub/main.py
# Filename: main.py

import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# It's good practice to load this at the very start
load_dotenv()

from app.services.nl_query_service import process_nl_query

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/api/v1/query', methods=['POST'])
def handle_query():
    """
    API endpoint to handle natural language queries.
    """
    if not request.json or 'query' not in request.json:
        return jsonify({"error": "Query not provided"}), 400
    
    query = request.json['query']
    result = process_nl_query(query)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

#end-of-file
