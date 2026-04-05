from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from routes import api_bp, init_network # Import Blueprint and init fn

app = Flask(__name__)
# Enable CORS for all routes (important for frontend requests)
CORS(app)

# Setup directories
backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(os.path.dirname(backend_dir), 'frontend')

# Register endpoints blueprint
app.register_blueprint(api_bp, url_prefix='/api')

# --- Frontend Routing (Static Files) ---
@app.route('/')
def home():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(frontend_dir, path)

# --- Backend Network Initialization ---
edges_path = os.path.join(backend_dir, 'dataset.csv')
nodes_path = os.path.join(backend_dir, 'nodes.csv')
init_network(edges_path, nodes_path)

if __name__ == '__main__':
    print("Starting Smart Disaster Response Routing System API...")
    app.run(host='0.0.0.0', port=5000, debug=True)
