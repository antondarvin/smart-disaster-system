from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Add current directory to sys.path to ensure absolute imports work on Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from routes import api_bp, init_network
except ImportError:
    from .routes import api_bp, init_network

app = Flask(__name__)
CORS(app)

# Use Pathlib for robust directory handling in Serverless
BASE_DIR = Path(__file__).resolve().parent

# Registration
app.register_blueprint(api_bp, url_prefix='/api')

# Initialize paths
edges_path = str(BASE_DIR / 'dataset.csv')
nodes_path = str(BASE_DIR / 'nodes.csv')

# Initialize network structure on first request for reliability
initialized = False
@app.before_request
def start_up():
    global initialized
    if not initialized:
        try:
            init_network(edges_path, nodes_path)
            initialized = True
        except Exception as e:
            print(f"LAZY INIT FAILED: {e}")

@app.route("/")
def home():
    return jsonify({"status": "healthy", "message": "Backend working!"})

# Expose app for Vercel
if __name__ == '__main__':
    print("Starting Smart Disaster Response Routing System API...")
    app.run(host='127.0.0.1', port=5000, debug=True)
