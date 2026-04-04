from flask import Flask
from flask_cors import CORS
import os
from routes import api_bp, init_network # Import Blueprint and init fn

app = Flask(__name__)
# Enable CORS for all routes (important for frontend requests)
CORS(app)

# Register endpoints blueprint
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    # Initialize the graph network paths
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    edges_path = os.path.join(backend_dir, 'dataset.csv')
    nodes_path = os.path.join(backend_dir, 'nodes.csv')
    
    # Init the network structure
    init_network(edges_path, nodes_path)
    print("Starting Smart Disaster Response Routing System API...")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
