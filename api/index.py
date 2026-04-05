from flask import Flask, jsonify
from flask_cors import CORS
import os
from routes import api_bp, init_network

app = Flask(__name__)
# Enable CORS for all routes (important for frontend requests)
CORS(app)

# Setup directories
backend_dir = os.path.dirname(os.path.abspath(__file__))

# Register endpoints blueprint
app.register_blueprint(api_bp, url_prefix='/api')

# --- Backend Network Initialization ---
edges_path = os.path.join(backend_dir, 'dataset.csv')
nodes_path = os.path.join(backend_dir, 'nodes.csv')
init_network(edges_path, nodes_path)

@app.route("/")
def home():
    return jsonify({"message": "Backend working!"})

# IMPORTANT for Vercel
def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    print("Starting Smart Disaster Response Routing System API...")
    app.run(host='127.0.0.1', port=5000, debug=True)
