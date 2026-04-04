from flask import Blueprint, jsonify, request
from graph_utils import DisasterNetwork

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize network structure globally
network = None

def init_network(edges_path, nodes_path):
    global network
    network = DisasterNetwork(edges_path, nodes_path)
    # Ensure graph is built successfully
    network._build_graph()

@api_bp.route('/load-data', methods=['GET'])
def load_data():
    """Loads dataset and returns nodes and edges."""
    if not network:
        return jsonify({"error": "Network not initialized"}), 500
        
    nodes = network.get_all_nodes()
    edges = network.get_all_edges()
    
    return jsonify({
        "nodes": nodes,
        "edges": edges,
        "message": "Data loaded successfully"
    })

@api_bp.route('/get-route', methods=['POST'])
def get_route():
    """Calculates the safest route based on vehicle capabilities."""
    data = request.json
    source = data.get('source')
    target = data.get('target')
    vehicle = data.get('vehicle', 'Rescue Truck') # default vehicle
    
    if not source or not target:
        return jsonify({"error": "Source and target are required"}), 400
        
    result = network.get_safest_route(source, target, vehicle)
    return jsonify(result)

@api_bp.route('/simulate', methods=['POST'])
def simulate():
    """Simulates a disaster by randomly changing road conditions."""
    if not network:
        return jsonify({"error": "Network not initialized"}), 500
        
    result = network.simulate_disaster()
    # Return new state representation
    edges = network.get_all_edges()
    return jsonify({
        "message": result["message"],
        "updates": result["updates"],
        "edges": edges
    })
