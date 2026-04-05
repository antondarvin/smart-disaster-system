from flask import Flask, jsonify
from flask_cors import CORS
import os
from pathlib import Path
from routes import api_bp, init_network

app = Flask(__name__)
CORS(app)

# Use Pathlib for robust directory handling in Serverless
BASE_DIR = Path(__file__).resolve().parent

# Registration
app.register_blueprint(api_bp, url_prefix='/api')

# Initialize network structure globally
edges_path = str(BASE_DIR / 'dataset.csv')
nodes_path = str(BASE_DIR / 'nodes.csv')

# Pre-initialize or handle it lazily
try:
    init_network(edges_path, nodes_path)
except Exception as e:
    print(f"FAILED TO INITIALIZE NETWORK: {e}")

@app.route("/")
def home():
    return jsonify({"message": "Backend working!"})

# Expose app for Vercel
# (The handler function is not strictly needed for Flask on Vercel)

if __name__ == '__main__':
    print("Starting Smart Disaster Response Routing System API...")
    app.run(host='127.0.0.1', port=5000, debug=True)
