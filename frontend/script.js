// Configuration
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Map Initialization
const map = L.map('map').setView([37.7760, -122.4080], 14);

// Tile Layer (Dark theme by default to match UI)
const tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO'
}).addTo(map);

// Global State
let networkData = { nodes: [], edges: [] };
let sourceSelection = null;
let targetSelection = null;
let edgeLayerGroup = L.layerGroup().addTo(map);
let nodeLayerGroup = L.layerGroup().addTo(map);
let routeLayerGroup = L.layerGroup().addTo(map);
let currentRouteLayer = null;

// DOM Elements
const sourceInput = document.getElementById('source-input');
const targetInput = document.getElementById('target-input');
const calcBtn = document.getElementById('calc-btn');
const simBtn = document.getElementById('sim-btn');
const vehicleSelect = document.getElementById('vehicle-select');
const outputPanel = document.getElementById('output-panel');
const themeToggle = document.getElementById('theme-toggle');

// Helper formatting functions
const getRiskColor = (risk_level) => {
    switch (risk_level) {
        case 'low': return '#22c55e'; // Green (Safe)
        case 'medium': return '#eab308'; // Yellow (Medium risk)
        case 'high': return '#ef4444'; // Red (Dangerous)
        default: return '#9ca3af';
    }
}

// Fetch Data & Initialize Map
async function loadData() {
    try {
        const res = await fetch(`${API_BASE_URL}/load-data`);
        const data = await res.json();
        if (data.error) throw new Error(data.error);

        networkData = data;
        renderNetwork();
    } catch (err) {
        console.error("Failed to load map data:", err);
        alert("Failed to load network data. Is the backend running?");
    }
}

// Render Graph Nodes and Edges
function renderNetwork() {
    edgeLayerGroup.clearLayers();
    nodeLayerGroup.clearLayers();

    // Render Edges
    networkData.edges.forEach(edge => {
        const latlngs = [
            [edge.source_coords.lat, edge.source_coords.lng],
            [edge.target_coords.lat, edge.target_coords.lng]
        ];

        const color = getRiskColor(edge.risk_level);
        const weight = edge.condition === 'blocked' ? 2 : 4;
        const dashArray = edge.condition === 'blocked' ? '4, 10' : null;

        const polyline = L.polyline(latlngs, {
            color: color,
            weight: weight,
            dashArray: dashArray,
            opacity: 0.7
        }).addTo(edgeLayerGroup);

        // Tooltip
        polyline.bindTooltip(`
            <b>${edge.source} &rarr; ${edge.target}</b><br>
            Condition: ${edge.condition}<br>
            Terrain: ${edge.terrain}<br>
            Risk: ${edge.risk_level}
        `);
    });

    // Render Nodes
    networkData.nodes.forEach(node => {
        const marker = L.circleMarker([node.lat, node.lng], {
            radius: 8,
            fillColor: '#3b82f6',
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
        }).addTo(nodeLayerGroup);

        marker.bindTooltip(`Node ${node.id}`, { permanent: true, direction: 'top', className: 'node-label' });

        // Click handler for selection
        marker.on('click', () => handleNodeSelection(node.id));
    });
}

// Handle Node Clicking (Source/Target Setup)
function handleNodeSelection(nodeId) {
    if (!sourceSelection || (sourceSelection && targetSelection)) {
        // Start fresh or reset
        sourceSelection = nodeId;
        targetSelection = null;
        sourceInput.value = nodeId;
        targetInput.value = '';
    } else if (sourceSelection && sourceSelection !== nodeId) {
        // Set target
        targetSelection = nodeId;
        targetInput.value = nodeId;
    }
}

// Calculate Best Route Execution
calcBtn.addEventListener('click', async () => {
    // Read from inputs in case user typed them
    const source = sourceInput.value.trim().toUpperCase();
    const target = targetInput.value.trim().toUpperCase();
    const vehicle = vehicleSelect.value;

    if (!source || !target) {
        alert("Please select both a Source and Destination node.");
        return;
    }

    // Call API
    try {
        const res = await fetch(`${API_BASE_URL}/get-route`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source, target, vehicle })
        });
        
        const data = await res.json();
        
        if (data.error) {
            handleErrorState(data.error);
        } else {
            displayRoute(data);
        }
    } catch (err) {
        console.error("Routing error:", err);
        alert("Failed to calculate route. See console.");
    }
});

// Display Route Output
function displayRoute(data) {
    routeLayerGroup.clearLayers();
    outputPanel.classList.add('active');

    // Update Output Metrics
    document.getElementById('out-distance').innerText = `${data.metrics.total_distance} units`;
    document.getElementById('out-time').innerText = `~${data.metrics.estimated_time} mins`;
    document.getElementById('out-risk').innerText = data.metrics.risk_score;
    
    const statusEl = document.getElementById('out-status');
    statusEl.innerText = `${data.metrics.vehicle} Valid`;
    statusEl.className = 'status-badge status-valid';

    // Draw Route Polyline
    const latlngs = data.coordinates.map(c => [c.lat, c.lng]);
    
    // Animate drawing
    currentRouteLayer = L.polyline(latlngs, {
        color: '#3b82f6',
        weight: 6,
        opacity: 0.9,
        lineCap: 'round',
        lineJoin: 'round',
        className: 'route-line-anim'
    }).addTo(routeLayerGroup);
    
    // Fit bounds 
    map.fitBounds(currentRouteLayer.getBounds(), { padding: [50, 50] });
}

// Handle Invalid Route State
function handleErrorState(errMsg) {
    routeLayerGroup.clearLayers();
    outputPanel.classList.add('active');
    
    document.getElementById('out-distance').innerText = `--`;
    document.getElementById('out-time').innerText = `--`;
    document.getElementById('out-risk').innerText = `--`;

    const statusEl = document.getElementById('out-status');
    statusEl.innerText = "No Valid Route";
    statusEl.className = 'status-badge status-invalid';

    alert(errMsg);
}

// Simulate Disaster
simBtn.addEventListener('click', async () => {
    try {
        const res = await fetch(`${API_BASE_URL}/simulate`, { method: 'POST' });
        const data = await res.json();
        
        if (data.error) throw new Error(data.error);
        
        // Update network data and re-render map
        networkData.edges = data.edges;
        renderNetwork();

        // If a route exists, recalculate to see if it's still valid
        if (currentRouteLayer && sourceInput.value && targetInput.value) {
            calcBtn.click(); // Auto-recalculate
        }

    } catch (err) {
        console.error("Simultion Error:", err);
    }
});

// Theme Toggling
themeToggle.addEventListener('click', () => {
    const htmlObj = document.documentElement;
    const isDark = htmlObj.getAttribute('data-theme') === 'dark';
    
    if (isDark) {
        htmlObj.setAttribute('data-theme', 'light');
        tileLayer.setUrl('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png');
    } else {
        htmlObj.setAttribute('data-theme', 'dark');
        tileLayer.setUrl('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png');
    }
});

// CSS Animation class logic
const style = document.createElement('style');
style.textContent = `
    .route-line-anim {
        stroke-dasharray: 1000;
        stroke-dashoffset: 1000;
        animation: dash 2s linear forwards;
    }
    .node-label {
        background: transparent;
        border: none;
        box-shadow: none;
        color: var(--text-color);
        font-weight: bold;
        text-shadow: 0 0 3px black;
    }
    @keyframes dash {
        to {
            stroke-dashoffset: 0;
        }
    }
`;
document.head.appendChild(style);

// Init
loadData();
