# Smart Disaster Response Routing System

A full-stack application designed to calculate the safest and most efficient routes for rescue vehicles during disaster conditions (floods, debris, blocked roads).

## Features
- **Dynamic Routing**: Uses Dijkstra/A* algorithms to find safe paths based on vehicle capabilities.
- **Risk Assessment**: Real-time visualization of road conditions (Low, Medium, High risk).
- **Interactive Map**: Powered by Leaflet.js with dark-mode glassmorphism UI.
- **Disaster Simulation**: Simulate random disaster events to test route resilience.
- **Vercel Optimized**: Fully compatible with Vercel Serverless Functions.

---

## Getting Started (Local Development)

### 1. Prerequisites
- Python 3.8 or higher.
- A modern web browser.

### 2. Backend Setup
1. Open your terminal in the project root directory.
2. (Optional but Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Flask server:
   ```bash
   python api/index.py
   ```
   *The backend will now be running at `http://127.0.0.1:5000`.*

### 3. Frontend Setup
Simply open the `frontend/index.html` file in your browser:
- You can right-click the file and select "Open with Browser".
- Or, if you use VS Code, use the **Live Server** extension for the best experience.

---

## Deployment (Vercel)

The project is pre-configured for Vercel:
1. Push your code to a GitHub repository.
2. Connect your repository to Vercel.
3. Vercel will automatically detect the `api/index.py` and `vercel.json` configuration.

---

## Project Structure
- `api/`: Python backend logic, algorithms, and datasets.
  - `index.py`: Entry point for the Flask application.
  - `routes.py`: API endpoint definitions.
  - `graph_utils.py`: Heart of the Dijkstra routing logic.
- `frontend/`: Clean HTML/CSS/JS files for the UI.
  - `script.js`: Map logic and API communication.
- `vercel.json`: Configuration for seamless production deployment.
