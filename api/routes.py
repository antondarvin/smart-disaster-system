from flask import Blueprint, jsonify, request
from graph_utils import DisasterNetwork

api_bp = Blueprint('api', __name__)
network = None

def init_network(edges_path, nodes_path):
    global network
    if network is None:
        network = DisasterNetwork(edges_path, nodes_path)

@api_bp.route('/load-data', methods=['GET'])
def load_data():
    if not network:
        return jsonify({"error": "Network data file not found on server"}), 500
    try:
        return jsonify({
            "nodes": network.get_all_nodes(),
            "edges": network.get_all_edges(),
            "message": "Data loaded successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/get-route', methods=['POST'])
def get_route():
    if not network: return jsonify({"error": "Server error: Network not ready"}), 500
    data = request.json
    source = data.get('source')
    target = data.get('target')
    vehicle = data.get('vehicle', 'Rescue Truck')
    
    if not source or not target:
        return jsonify({"error": "Source and target are required"}), 400
        
    return jsonify(network.get_safest_route(source, target, vehicle))

@api_bp.route('/simulate', methods=['POST'])
def simulate():
    if not network: return jsonify({"error": "Server error: Network not ready"}), 500
    result = network.simulate_disaster()
    return jsonify({
        "message": result["message"],
        "updates": result["updates"],
        "edges": network.get_all_edges()
    })
