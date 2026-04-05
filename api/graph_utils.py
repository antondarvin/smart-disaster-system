import csv
import networkx as nx
import random

# Weights configuration
CONDITION_WEIGHTS = {
    'clear': 1,
    'debris': 5,
    'flooded': 8,
    'blocked': float('inf')
}

RISK_WEIGHTS = {
    'low': 1,
    'medium': 3,
    'high': 6
}

TERRAIN_WEIGHTS = {
    'easy': 1,
    'medium': 2,
    'hard': 4
}

class DisasterNetwork:
    def __init__(self, edges_file, nodes_file):
        self.edges_file = edges_file
        self.nodes_file = nodes_file
        self.graph = nx.Graph()
        self.load_data()

    def load_data(self):
        """Loads nodes and edges from CSV files and builds the graph using built-in csv module."""
        self.graph.clear()
        
        # Load Nodes
        with open(self.nodes_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.graph.add_node(
                    row['node_id'], 
                    lat=float(row['lat']), 
                    lng=float(row['lng'])
                )
            
        # Load Edges
        with open(self.edges_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.graph.add_edge(
                    row['source_node'], 
                    row['destination_node'], 
                    distance=float(row['distance']),
                    condition=row['condition'],
                    risk_level=row['risk_level'],
                    terrain=row['terrain']
                )

    def calculate_edge_cost(self, u, v, vehicle_type):
        """Calculates the cost of an edge based on disaster conditions and vehicle capability."""
        edge = self.graph[u][v]
        
        cond = edge['condition']
        
        # Vehicle validation
        if vehicle_type == 'Ambulance' and cond != 'clear':
            return float('inf')
        elif vehicle_type == 'Rescue Truck' and cond not in ['clear', 'debris']:
            return float('inf')
        elif vehicle_type == 'Bulldozer' and cond == 'blocked':
            return float('inf')
            
        condition_cost = CONDITION_WEIGHTS.get(cond, float('inf'))
        if condition_cost == float('inf'):
            return float('inf')
            
        risk_cost = RISK_WEIGHTS.get(edge['risk_level'], 3)
        terrain_cost = TERRAIN_WEIGHTS.get(edge['terrain'], 2)
        
        total_cost = edge['distance'] + condition_cost + risk_cost + terrain_cost
        return total_cost

    def get_safest_route(self, source, target, vehicle_type):
        """Uses Dijkstra's algorithm to find the safest route."""
        if source not in self.graph or target not in self.graph:
            return {"error": "Invalid source or target node"}

        def weight_func(u, v, d):
            return self.calculate_edge_cost(u, v, vehicle_type)

        try:
            path = nx.dijkstra_path(self.graph, source, target, weight=weight_func)
            
            # Calculate total metrics along the path
            total_dist = 0
            risk_score = 0
            time_estimate = 0
            path_details = []
            
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                edge = self.graph[u][v]
                total_dist += edge['distance']
                risk_score += RISK_WEIGHTS.get(edge['risk_level'], 3)
                # Roughly estimate time based on terrain and condition
                speed_factor = 1.0
                if edge['terrain'] == 'hard': speed_factor = 0.5
                elif edge['terrain'] == 'medium': speed_factor = 0.8
                
                if edge['condition'] == 'debris': speed_factor *= 0.6
                elif edge['condition'] == 'flooded': speed_factor *= 0.3
                
                time_estimate += (edge['distance'] / speed_factor) * 10 # dummy conversion
                
                path_details.append({
                    "from": u,
                    "to": v,
                    "distance": edge['distance'],
                    "condition": edge['condition'],
                    "risk_level": edge['risk_level'],
                    "terrain": edge['terrain']
                })
                
            nodes_coords = [{"id": n, "lat": self.graph.nodes[n]['lat'], "lng": self.graph.nodes[n]['lng']} for n in path]

            return {
                "path": path,
                "coordinates": nodes_coords,
                "metrics": {
                    "total_distance": round(total_dist, 2),
                    "estimated_time": round(time_estimate, 1), # minutes
                    "risk_score": risk_score,
                    "vehicle": vehicle_type
                },
                "details": path_details
            }
        except nx.NetworkXNoPath:
            return {"error": "No valid route found for this vehicle. Try a different vehicle."}

    def simulate_disaster(self):
        """Randomly degrades road conditions."""
        conditions = ['clear', 'debris', 'flooded', 'blocked']
        weights = [0.4, 0.3, 0.2, 0.1]
        
        updates = []
        
        # Iterate through graph edges to update conditions
        for u, v in self.graph.edges():
            # Randomly worsen condition for a subset of edges
            if random.random() < 0.3: # 30% chance to change
                new_cond = random.choices(conditions, weights=weights)[0]
                self.graph[u][v]['condition'] = new_cond
                updates.append({"source": u, "target": v, "new_condition": new_cond})
                
        return {"message": "Disaster conditions updated", "updates": updates}

    def get_all_edges(self):
        """Returns all edges for frontend visualization."""
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "source_coords": {"lat": self.graph.nodes[u]['lat'], "lng": self.graph.nodes[u]['lng']},
                "target_coords": {"lat": self.graph.nodes[v]['lat'], "lng": self.graph.nodes[v]['lng']},
                "condition": data['condition'],
                "risk_level": data['risk_level'],
                "terrain": data['terrain']
            })
        return edges
        
    def get_all_nodes(self):
        nodes = []
        for node, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node,
                "lat": data['lat'],
                "lng": data['lng']
            })
        return nodes
