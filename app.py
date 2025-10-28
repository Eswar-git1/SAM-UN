from flask import Flask, jsonify, render_template, request, send_from_directory, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from functools import wraps
import os
import subprocess
import json
import requests
import sqlite3
from werkzeug.utils import secure_filename
import geopandas as gpd
from flask_cors import CORS
from chatbot import SitrepChatbot
from config import get_config
from supabase_client import (
    get_sitreps, insert_sitrep, update_sitrep, delete_sitrep,
    upload_layer_to_bucket, download_layer_from_bucket, 
    list_layers_in_bucket, delete_layer_from_bucket, update_layer_in_bucket,
    authenticate_user, create_user, get_user_by_username
)
from dotenv import load_dotenv
from llm_client import create_llm_client

# Load environment variables
load_dotenv(override=True)

# Get configuration based on environment
config_class = get_config()
app = Flask(__name__)
app.config.from_object(config_class)

# Configure CORS with environment-specific origins
CORS(app, origins=app.config['CORS_ORIGINS'])
socketio = SocketIO(app, cors_allowed_origins=app.config['CORS_ORIGINS'])

# Session activity tracking middleware
@app.before_request
def refresh_session():
    """Refresh session timeout on each request for logged-in users"""
    if 'user_id' in session:
        session.permanent = True

# Directories
geojson_dir = os.path.join(os.path.dirname(__file__), "Assignment", "GeoJSON Output")
upload_dir = app.config['UPLOAD_FOLDER']

# Database is now handled by Supabase
DB_PATH = app.config['DATABASE_URL']  # Keep for compatibility with existing code

# Ensure directories exist
os.makedirs(geojson_dir, exist_ok=True)
os.makedirs(upload_dir, exist_ok=True)

# No need to initialize database as tables are created in Supabase

# Initialize chatbot with appropriate LLM provider
def create_chatbot():
    """Create chatbot with LLM configured from environment (OpenRouter only)"""
    try:
        provider = 'openrouter'
        llm = create_llm_client(
            provider,
            api_key=app.config.get('OPENROUTER_API_KEY'),
            base_url=app.config.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'),
            model_name=app.config.get('DEFAULT_MODEL')
        )
        # Pass configured LLM into chatbot via llm_config
        return SitrepChatbot(llm_provider=provider, llm_config={'client': llm})
    except Exception as e:
        # Fallback to chatbot without LLM
        print(f"LLM init failed; chatbot starting without LLM: {e}")
        return SitrepChatbot()

chatbot = create_chatbot()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')
        
        # Authenticate user
        user = authenticate_user(username, password)
        if user:
            session.permanent = True  # Enable session timeout
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html')
    
    # If user is already logged in, redirect to main page
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/health')
def health_check():
    """Health check endpoint for Railway deployment"""
    return jsonify({
        "status": "healthy",
        "message": "SAM UN application is running",
        "version": "1.0.0"
    }), 200

@app.route('/')
@login_required
def index():
    return render_template('index.html', config=app.config)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat messages and return AI responses"""
    data = request.json
    message = data.get('message', '')
    
    # Get response from chatbot using process_query method
    result = chatbot.process_query(message)
    
    # Extract relevant information from the result
    response = {
        "message": f"I found information about your query: {message}",
        "data": result.get("data", []),
        "count": len(result.get("data", []))
    }
    
    return jsonify({"response": response})

@app.route('/api/sitrep_geojson')
def get_sitrep_geojson():
    """Return all sitreps as GeoJSON for map display"""
    sitreps = get_sitreps()
    
    # Create GeoJSON structure
    features = []
    for i, sitrep in enumerate(sitreps):
        # Use default coordinates for Congo if none exist
        lat = sitrep.get('latitude')
        lon = sitrep.get('longitude')
        
        # If coordinates are missing, generate some in Congo region
        if not lat or not lon:
            lat = -2.5 + (i * 0.05)  # Default coordinates for Congo
            lon = 28.8 + (i * 0.05)  # Default coordinates for Congo
            
        # Create GeoJSON feature
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(lon), float(lat)]
            },
            "properties": {
                "id": sitrep.get('id'),
                "title": sitrep.get('title', ''),
                "content": sitrep.get('content', ''),
                "priority": sitrep.get('priority', ''),
                "status": sitrep.get('status', ''),
                "timestamp": sitrep.get('timestamp', ''),
                "source": sitrep.get('source', ''),
                "source_category": sitrep.get('source_category', ''),
                "incident_type": sitrep.get('incident_type', '')
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return jsonify(geojson)

# Whitelisted vendor packages served from node_modules
ALLOWED_VENDOR_PACKAGES = {
    'leaflet': os.path.join(os.path.dirname(__file__), 'node_modules', 'leaflet'),
    'leaflet-draw': os.path.join(os.path.dirname(__file__), 'node_modules', 'leaflet-draw'),
    'leaflet.browser.print': os.path.join(os.path.dirname(__file__), 'node_modules', 'leaflet.browser.print'),
    'leaflet.vectorgrid': os.path.join(os.path.dirname(__file__), 'node_modules', 'leaflet.vectorgrid'),
    'leaflet.heat': os.path.join(os.path.dirname(__file__), 'node_modules', 'leaflet.heat'),
    'togeojson': os.path.join(os.path.dirname(__file__), 'node_modules', 'togeojson'),
    'jszip': os.path.join(os.path.dirname(__file__), 'node_modules', 'jszip'),
    'pako': os.path.join(os.path.dirname(__file__), 'node_modules', 'pako'),
    'geotiff': os.path.join(os.path.dirname(__file__), 'node_modules', 'geotiff'),
    'georaster': os.path.join(os.path.dirname(__file__), 'node_modules', 'georaster'),
    'georaster-layer-for-leaflet': os.path.join(os.path.dirname(__file__), 'node_modules', 'georaster-layer-for-leaflet'),
    '@ngageoint/geopackage': os.path.join(os.path.dirname(__file__), 'node_modules', '@ngageoint', 'geopackage'),
    'sql.js': os.path.join(os.path.dirname(__file__), 'node_modules', 'sql.js'),
    'chart.js': os.path.join(os.path.dirname(__file__), 'node_modules', 'chart.js'),
}

@app.route('/vendor/<path:subpath>')
def serve_vendor(subpath):
    # Support scoped packages like @scope/name by splitting the subpath
    parts = [p for p in subpath.split('/') if p]
    if not parts:
        return {"error": "Invalid request"}, 404
    if parts[0].startswith('@'):
        if len(parts) < 2:
            return {"error": "Invalid request"}, 404
        package_key = parts[0] + '/' + parts[1]
        filename_parts = parts[2:]
    else:
        package_key = parts[0]
        filename_parts = parts[1:]

    # Only serve from whitelisted packages
    base_dir = ALLOWED_VENDOR_PACKAGES.get(package_key)
    if not base_dir:
        return {"error": "Package not allowed"}, 404

    filename = '/'.join(filename_parts)
    # Prevent path traversal
    safe_path = os.path.normpath(os.path.join(base_dir, filename))
    if not safe_path.startswith(base_dir):
        return {"error": "Invalid path"}, 400
    if not os.path.exists(safe_path):
        return {"error": "File not found"}, 404
    # Serve file
    rel_dir = os.path.dirname(os.path.relpath(safe_path, base_dir))
    rel_file = os.path.basename(safe_path)
    # send_from_directory requires directory + filename
    return send_from_directory(os.path.join(base_dir, rel_dir), rel_file)

# SITREP API: list and create
@app.route('/api/sitreps', methods=['GET', 'POST'])
def api_sitreps():
    if request.method == 'GET':
        # Get filters from query parameters
        filters = {}
        if request.args.get('from_date'):
            filters['from_date'] = request.args.get('from_date')
        if request.args.get('to_date'):
            filters['to_date'] = request.args.get('to_date')
        if request.args.get('source_category'):
            filters['source_category'] = request.args.get('source_category')
            
        # Use Supabase client to get sitreps
        rows = get_sitreps(filters)
        return jsonify(rows)
    else:
        data = request.json or {}
        required = ['source', 'lat', 'lon']
        for k in required:
            if k not in data or data[k] in (None, ""):
                return {"error": f"Missing required field: {k}"}, 400
        try:
            lat = float(data['lat'])
            lon = float(data['lon'])
        except Exception:
            return {"error": "lat/lon must be numbers"}, 400
            
        # Prepare data for Supabase
        sitrep_data = {
            'source': str(data.get('source', '')).strip(),
            'source_category': str(data.get('source_category', '')).strip().lower(),
            'incident_type': str(data.get('incident_type', '')).strip().lower(),
            'title': str(data.get('title', '')).strip() or "Untitled",
            'description': str(data.get('description', '')).strip() or "No description provided",
            'severity': str(data.get('severity', 'Unknown')).strip(),
            'status': str(data.get('status', '')).strip().lower(),
            'unit': str(data.get('unit', '')).strip(),
            'contact': str(data.get('contact', '')).strip(),
            'lat': lat,
            'lon': lon
        }
        
        # Use Supabase client to insert sitrep
        result = insert_sitrep(sitrep_data)
        return result

# SITREP GeoJSON view for direct map consumption with filters
@app.route('/api/sitreps.geojson', methods=['GET'])
def api_sitreps_geojson():
    # Build filters from query parameters, supporting both snake_case and camelCase
    filters = {}

    # Accept either from_date or fromDate
    from_date = request.args.get('from_date') or request.args.get('fromDate')
    to_date = request.args.get('to_date') or request.args.get('toDate')
    sources = request.args.get('source_category') or request.args.get('sources')
    range_days = request.args.get('rangeDays')

    # Convert rangeDays to from_date ISO cutoff
    if range_days and not from_date:
        try:
            days = int(range_days)
            cutoff = datetime.utcnow() - timedelta(days=days)
            filters['from_date'] = cutoff.replace(microsecond=0).isoformat() + 'Z'
        except Exception:
            pass

    # Normalize date-only values to full-day ISO
    if from_date:
        # If already contains 'T', assume ISO timestamp and pass through
        filters['from_date'] = from_date if 'T' in from_date else f"{from_date}T00:00:00Z"
    if to_date:
        filters['to_date'] = to_date if 'T' in to_date else f"{to_date}T23:59:59Z"

    # Map sources/source_category to Supabase filter
    if sources:
        filters['source_category'] = sources
        
    # Use Supabase client to get sitreps
    sitreps = get_sitreps(filters)
    
    # Convert to GeoJSON format
    features = []
    for sitrep in sitreps:
        # Handle field name differences between SQLite and Supabase
        description = sitrep.get('content', sitrep.get('description', ''))
        
        # Check if coordinates exist, use default values if not
        lon = sitrep.get('lon', sitrep.get('longitude'))
        lat = sitrep.get('lat', sitrep.get('latitude'))
        
        # If still no coordinates, use default values for Congo region
        if lon is None or lat is None:
            # Default to Congo region with slight offset to avoid overlapping points
            lon = 15.2827 + (sitrep['id'] % 100) * 0.01
            lat = -4.2634 + (sitrep['id'] % 100) * 0.01
            
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "id": sitrep['id'],
                "source": sitrep['source'],
                "source_category": sitrep.get('source_category', ''),
                "incident_type": sitrep.get('incident_type', ''),
                "title": sitrep.get('title', ''),
                "description": description,
                "severity": sitrep.get('severity', 'Unknown'),
                "status": sitrep.get('status', ''),
                "unit": sitrep.get('unit', ''),
                "contact": sitrep.get('contact', ''),
                "created_at": sitrep.get('created_at', sitrep.get('timestamp', ''))
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return jsonify(geojson)
    conditions = []
    params = []

    range_days = request.args.get('rangeDays')
    if range_days:
        try:
            days = int(range_days)
            # created_at is ISO timestamp; use SQLite datetime() for relative range
            conditions.append("created_at >= datetime('now', ?)")
            params.append(f"-{days} days")
        except Exception:
            pass

    from_date = request.args.get('fromDate')
    if from_date:
        # Start of day
        conditions.append("created_at >= ?")
        params.append(from_date + " 00:00:00")

    to_date = request.args.get('toDate')
    if to_date:
        # End of day
        conditions.append("created_at <= ?")
        params.append(to_date + " 23:59:59")

    sources = request.args.get('sources')
    if sources:
        values = [s.strip().lower() for s in sources.split(',') if s.strip()]
        if values:
            placeholders = ",".join(["?"] * len(values))
            # Filter by source_category instead of free-text source name
            conditions.append(f"LOWER(source_category) IN ({placeholders})")
            params.extend(values)

    base_sql = "SELECT id, source, source_category, incident_type, title, description, severity, lat, lon, created_at, status, unit, contact FROM sitreps"
    if conditions:
        where_sql = " WHERE " + " AND ".join(conditions)
    else:
        where_sql = ""
    order_sql = " ORDER BY created_at DESC"
    sql = base_sql + where_sql + order_sql

    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row['lon'], row['lat']]},
                "properties": {
                    "id": row['id'],
                    "source": row['source'],
                    "source_category": row.get('source_category'),
                    "incident_type": row.get('incident_type'),
                    "title": row['title'],
                    "description": row['description'],
                    "severity": row['severity'],
                    "status": row.get('status'),
                    "unit": row.get('unit'),
                    "contact": row.get('contact'),
                    "created_at": row['created_at']
                }
            }
            for row in rows
        ]
    }
    return jsonify(fc)

# Heat map API endpoint for source-wise incident density
@app.route('/api/sitreps/heatmap', methods=['GET'])
def api_sitreps_heatmap():
    """
    Generate heat map data for incidents filtered by source.
    Returns aggregated incident counts in geographic grid cells.
    """
    try:
        print(f"Heatmap API called with args: {dict(request.args)}")
        
        # Build filters for Supabase query
        filters = {}
        
        # Date range filters
        range_days = request.args.get('rangeDays')
        if range_days:
            try:
                days = int(range_days)
                from datetime import datetime, timedelta
                cutoff = datetime.utcnow() - timedelta(days=days)
                filters['from_date'] = cutoff.replace(microsecond=0).isoformat() + 'Z'
                print(f"Applied range filter: {days} days, from_date: {filters['from_date']}")
            except Exception as e:
                print(f"Error parsing range_days: {e}")

        from_date = request.args.get('fromDate') or request.args.get('from_date') or request.args.get('start_date')
        if from_date:
            filters['from_date'] = from_date if 'T' in from_date else f"{from_date}T00:00:00Z"
            print(f"Applied from_date filter: {filters['from_date']}")

        to_date = request.args.get('toDate') or request.args.get('to_date') or request.args.get('end_date')
        if to_date:
            filters['to_date'] = to_date if 'T' in to_date else f"{to_date}T23:59:59Z"
            print(f"Applied to_date filter: {filters['to_date']}")

        # Source filter
        sources = request.args.get('sources')
        source_filter = None
        if sources:
            values = [s.strip().lower() for s in sources.split(',') if s.strip()]
            if values:
                filters['source_category'] = ','.join(values)
                source_filter = values
                print(f"Applied source filter: {source_filter}")

        print(f"Final filters for Supabase: {filters}")

        # Get sitreps from Supabase
        print("Calling get_sitreps with filters...")
        sitreps = get_sitreps(filters)
        print(f"Retrieved {len(sitreps) if sitreps else 0} sitreps from Supabase")
        
        # Convert to the format expected by the rest of the function
        rows = []
        for sitrep in sitreps:
            # Check if lat/lon are valid
            lat = sitrep.get('lat')
            lon = sitrep.get('lon')
            
            if lat is None or lon is None:
                print(f"Skipping sitrep with missing coordinates: lat={lat}, lon={lon}")
                continue
                
            try:
                lat = float(lat)
                lon = float(lon)
            except (ValueError, TypeError) as e:
                print(f"Skipping sitrep with invalid coordinates: lat={lat}, lon={lon}, error={e}")
                continue
            
            # Calculate weight based on severity
            severity = (sitrep.get('severity') or 'unknown').lower()
            if severity == 'critical':
                weight = 5
            elif severity == 'high':
                weight = 4
            elif severity == 'medium':
                weight = 3
            elif severity == 'low':
                weight = 2
            else:
                weight = 1
                
            rows.append({
                'lat': lat,
                'lon': lon,
                'severity': sitrep.get('severity'),
                'source_category': sitrep.get('source_category'),
                'weight': weight
            })
        
        print(f"Processed {len(rows)} valid sitreps for heatmap")
    
    except Exception as e:
        print(f"Error in heatmap API data processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch heatmap data: {str(e)}"}), 500

    # Grid-based aggregation for heat map
    try:
        grid_size = float(request.args.get('gridSize', 0.1))  # Default 0.1 degree grid
        print(f"Using grid size: {grid_size}")
        grid_data = {}
        
        for i, row in enumerate(rows):
            try:
                # Round coordinates to grid
                grid_lat = round(row['lat'] / grid_size) * grid_size
                grid_lon = round(row['lon'] / grid_size) * grid_size
                grid_key = f"{grid_lat},{grid_lon}"
                
                if grid_key not in grid_data:
                    grid_data[grid_key] = {
                        'lat': grid_lat,
                        'lon': grid_lon,
                        'count': 0,
                        'weight': 0,
                        'sources': {},
                        'severity_breakdown': {}
                    }
                
                grid_data[grid_key]['count'] += 1
                grid_data[grid_key]['weight'] += row['weight']
                
                # Track source distribution
                source = row['source_category'] or 'unknown'
                if source not in grid_data[grid_key]['sources']:
                    grid_data[grid_key]['sources'][source] = 0
                grid_data[grid_key]['sources'][source] += 1
                
                # Track severity distribution
                severity = row['severity'] or 'unknown'
                if severity not in grid_data[grid_key]['severity_breakdown']:
                    grid_data[grid_key]['severity_breakdown'][severity] = 0
                grid_data[grid_key]['severity_breakdown'][severity] += 1
                
            except Exception as e:
                print(f"Error processing row {i}: {e}, row data: {row}")
                continue

        print(f"Created {len(grid_data)} grid cells from {len(rows)} incidents")

        # Convert to heat map format
        heat_points = []
        for grid_key, data in grid_data.items():
            try:
                # Calculate intensity based on weighted count
                intensity = min(data['weight'] / 10.0, 1.0)  # Normalize to 0-1
                
                heat_points.append({
                    'lat': data['lat'],
                    'lng': data['lon'],
                    'intensity': intensity,
                    'count': data['count'],
                    'weight': data['weight'],
                    'sources': data['sources'],
                    'severity_breakdown': data['severity_breakdown'],
                    'dominant_source': max(data['sources'].items(), key=lambda x: x[1])[0] if data['sources'] else 'unknown'
                })
            except Exception as e:
                print(f"Error creating heat point for grid {grid_key}: {e}")
                continue

        # Sort by intensity to identify most critical areas
        heat_points.sort(key=lambda x: x['intensity'], reverse=True)
        
        print(f"Generated {len(heat_points)} heat points")

        response_data = {
            'heatPoints': heat_points,
            'metadata': {
                'totalIncidents': len(rows),
                'gridSize': grid_size,
                'sourceFilter': source_filter,
                'criticalAreas': heat_points[:10]  # Top 10 most critical areas
            }
        }
        
        print("Heatmap API completed successfully")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in heatmap grid processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to process heatmap grid: {str(e)}"}), 500

@app.route('/data/<layer>')
def get_geojson(layer):
    # Try to get from Supabase bucket first
    try:
        result = download_layer_from_bucket(layer)
        if result.get("success"):
            return jsonify(result["data"])
    except Exception as e:
        print(f"Supabase download failed for {layer}: {e}")
    
    # Fallback to local file
    file_path = os.path.join(geojson_dir, f"{layer}.geojson")
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                geojson_data = json.load(file)
                return jsonify(geojson_data)
        except UnicodeDecodeError:
            return {"error": f"File encoding issue with layer: {layer}"}, 500
    return {"error": "Layer not found"}, 404

@app.route('/data/layers')
def list_layers():
    # Try to get layers from Supabase bucket first
    try:
        result = list_layers_in_bucket()
        if result.get("success"):
            return jsonify(result["layers"])
    except Exception as e:
        print(f"Supabase list failed: {e}")
    
    # Fallback to local directory
    layers = [f.replace('.geojson', '') for f in os.listdir(geojson_dir) if f.endswith('.geojson')]
    return jsonify(layers)

@app.route('/data/<layer>/update', methods=['POST'])
def update_layer(layer):
    """
    Receives JSON: { "features": [ ...features with updated properties... ] }
    Updates the layer in Supabase bucket or local file.
    """
    data = request.json  # expects { "features": [ ... ] }
    if not data or "features" not in data:
        return {"error": "Invalid data format"}, 400

    # Try to upload/update in Supabase bucket first
    try:
        # Create complete GeoJSON structure
        geojson_data = {
            "type": "FeatureCollection",
            "features": data["features"]
        }
        
        result = upload_layer_to_bucket(layer, geojson_data)
        if result.get("success"):
            return {"status": "success", "updatedCount": len(data["features"]), "storage": "supabase"}
    except Exception as e:
        print(f"Supabase upload failed for {layer}: {e}")

    # Fallback to local file storage
    file_path = os.path.join(geojson_dir, f"{layer}.geojson")
    
    try:
        # If file exists, update it; otherwise create new
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                old_content = json.load(f)  # parse as dict
            if "features" not in old_content:
                return {"error": "Invalid existing geojson"}, 400
            # Overwrite features fully from client
            old_content["features"] = data["features"]
        else:
            # Create new GeoJSON file
            old_content = {
                "type": "FeatureCollection",
                "features": data["features"]
            }

        # Write back
        os.makedirs(geojson_dir, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(old_content, f, ensure_ascii=False, indent=2)

        return {"status": "success", "updatedCount": len(data["features"]), "storage": "local"}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/data/<layer>/delete', methods=['DELETE'])
def delete_layer(layer):
    """
    Delete a layer from Supabase bucket and/or local storage
    """
    try:
        # Try to delete from Supabase bucket first
        result = delete_layer_from_bucket(layer)
        supabase_deleted = result.get("success", False)
        
        # Also try to delete from local storage
        file_path = os.path.join(geojson_dir, f"{layer}.geojson")
        local_deleted = False
        if os.path.exists(file_path):
            os.remove(file_path)
            local_deleted = True
        
        if supabase_deleted or local_deleted:
            storage_info = []
            if supabase_deleted:
                storage_info.append("supabase")
            if local_deleted:
                storage_info.append("local")
            
            return {"status": "success", "message": f"Layer {layer} deleted", "storage": storage_info}
        else:
            return {"error": "Layer not found in any storage"}, 404
            
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/convert', methods=['POST'])
def convert_to_geojson():
    """Convert uploaded files to GeoJSON and save them to Supabase bucket (with local fallback)."""
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]
    if not file:
        return {"error": "No file selected"}, 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    try:
        # Determine file type by extension
        ext = os.path.splitext(filename)[1].lower()
        layer_name = os.path.splitext(filename)[0]
        output_file = os.path.join(geojson_dir, f"{layer_name}.geojson")

        # Convert to GeoDataFrame
        if ext == ".gpkg":
            gdf = gpd.read_file(file_path)
        elif ext == ".shp":
            # Check for required auxiliary files
            base_name = os.path.splitext(file_path)[0]
            shx_file = f"{base_name}.shx"
            dbf_file = f"{base_name}.dbf"
            if not os.path.exists(shx_file) or not os.path.exists(dbf_file):
                return {"error": "Shapefile requires .shp, .shx, and .dbf files."}, 400
            gdf = gpd.read_file(file_path)
        elif ext == ".csv":
            gdf = gpd.GeoDataFrame.from_file(file_path)  # Ensure CSV has lat/lon columns
        else:
            return {"error": f"Unsupported file format: {ext}"}, 400

        # Convert to GeoJSON format
        geojson_str = gdf.to_json()
        geojson_data = json.loads(geojson_str)
        
        # Try to save to Supabase bucket first
        storage_location = "local"
        try:
            success = upload_layer_to_bucket(layer_name, geojson_data)
            if success:
                storage_location = "supabase"
                print(f"✅ Layer '{layer_name}' uploaded to Supabase bucket successfully")
            else:
                print(f"⚠️ Failed to upload '{layer_name}' to Supabase, falling back to local storage")
                # Save to local file as fallback
                gdf.to_file(output_file, driver="GeoJSON")
        except Exception as e:
            print(f"⚠️ Error uploading '{layer_name}' to Supabase: {e}, falling back to local storage")
            # Save to local file as fallback
            gdf.to_file(output_file, driver="GeoJSON")

        return {
            "status": "success", 
            "geojson_file": f"{layer_name}.geojson",
            "layer_name": layer_name,
            "storage": storage_location,
            "features_count": len(geojson_data.get("features", []))
        }
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

import random
from datetime import datetime, timedelta

CONGO_BOUNDS = {
    "min_lat": -13.0,  # south
    "max_lat": 5.0,    # north
    "min_lon": 12.0,   # west
    "max_lon": 31.0,   # east
}

@app.route('/admin/seed_sitreps')
def seed_sitreps():
    """Seed at least 150 SITREPs in the last 90 days for all source categories within Congo bounds."""
    categories = ["own", "local", "rebel", "ngo", "other"]
    statuses = ["reported", "confirmed", "ongoing", "resolved"]
    severities = ["Low", "Medium", "High", "Critical"]
    titles = [
        "Patrol report", "Supply disruption", "Civilians displaced", "Skirmish reported",
        "Aid convoy movement", "Bridge damage", "Check-point established", "Medical incident"
    ]
    descriptions = [
        "Observed activity in sector.", "Infrastructure issue noted.", "Security update received.",
        "Humanitarian situation assessed.", "Local authority communication.", "Reconnaissance summary."
    ]
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    count = cur.execute("SELECT COUNT(*) FROM sitreps").fetchone()[0]
    needed = max(0, 150 - count)
    for i in range(needed):
        days_back = random.randint(0, 89)
        created = datetime.utcnow() - timedelta(days=days_back, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        cat = random.choice(categories)
        status = random.choice(statuses)
        severity = random.choice(severities)
        lat = random.uniform(CONGO_BOUNDS["min_lat"], CONGO_BOUNDS["max_lat"])
        lon = random.uniform(CONGO_BOUNDS["min_lon"], CONGO_BOUNDS["max_lon"])
        title = random.choice(titles)
        desc = random.choice(descriptions)
        source = {
            "own": "HQ / Own Forces",
            "local": "Local Govt",
            "rebel": "Rebel Group",
            "ngo": "NGO Partner",
            "other": "Other Source",
        }[cat]
        unit = f"Unit {random.randint(1, 20)}"
        contact = f"POC {random.randint(100,999)}-555-{random.randint(1000,9999)}"
        cur.execute(
            "INSERT INTO sitreps (source, source_category, title, description, severity, status, unit, contact, lat, lon, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (source, cat, title, desc, severity, status, unit, contact, lat, lon, created.strftime("%Y-%m-%d %H:%M:%S"))
        )
    conn.commit()
    conn.close()
    return {"status": "seeded", "added": needed}

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/sitreps/stats', methods=['GET'])
def api_sitreps_stats():
    """Return aggregated SITREP stats using Supabase, with optional filters.
    Supports query params: rangeDays, fromDate, toDate, sources (comma-separated categories).
    Also supports existing params: from_date, to_date, source_category.
    """
    try:
        # Build filters in Supabase format
        filters = {}
    
        # Support both camelCase and snake_case params
        from_date = request.args.get('fromDate') or request.args.get('from_date')
        to_date = request.args.get('toDate') or request.args.get('to_date')
        sources = request.args.get('sources') or request.args.get('source_category')
        range_days = request.args.get('rangeDays')
    
        # rangeDays -> from_date
        if range_days:
            try:
                days = int(range_days)
                cutoff = datetime.utcnow() - timedelta(days=days)
                # ISO format without microseconds for Supabase filter
                filters['from_date'] = cutoff.replace(microsecond=0).isoformat() + 'Z'
            except Exception:
                pass
    
        if from_date:
            # assume date-only string; start of day in ISO
            filters['from_date'] = f"{from_date}T00:00:00Z"
        if to_date:
            # end of day; use 23:59:59
            filters['to_date'] = f"{to_date}T23:59:59Z"
        if sources:
            # Pass through as comma-separated for supabase_client to split
            filters['source_category'] = sources
    
        # Fetch sitreps from Supabase
        rows = get_sitreps(filters) or []
    
        # Helpers
        def parse_date(dt_str):
            if not dt_str:
                return None
            try:
                # Normalize potential 'Z' timezone
                clean = dt_str.replace('Z', '')
                return datetime.fromisoformat(clean)
            except Exception:
                return None
    
        # Compute total
        total = len(rows)
    
        # By day
        counts_by_day = {}
        for r in rows:
            d = parse_date(r.get('created_at'))
            if d:
                day_key = d.date().isoformat()
                counts_by_day[day_key] = counts_by_day.get(day_key, 0) + 1
        by_day = [{"day": k, "count": v} for k, v in sorted(counts_by_day.items())]
    
        # Severity
        counts_sev = {}
        for r in rows:
            sev = (r.get('severity') or 'unknown').lower()
            counts_sev[sev] = counts_sev.get(sev, 0) + 1
        by_severity = [{"severity": k, "count": v} for k, v in sorted(counts_sev.items(), key=lambda x: x[1], reverse=True)]
    
        # Source category
        counts_src = {}
        for r in rows:
            src = (r.get('source_category') or 'other').lower()
            counts_src[src] = counts_src.get(src, 0) + 1
        by_source_category = [{"source_category": k, "count": v} for k, v in sorted(counts_src.items(), key=lambda x: x[1], reverse=True)]
    
        # Status
        counts_status = {}
        for r in rows:
            st = (r.get('status') or 'unknown').lower()
            counts_status[st] = counts_status.get(st, 0) + 1
        by_status = [{"status": k, "count": v} for k, v in sorted(counts_status.items(), key=lambda x: x[1], reverse=True)]
    
        # Top units
        counts_units = {}
        for r in rows:
            unit = r.get('unit') or 'Unspecified'
            counts_units[unit] = counts_units.get(unit, 0) + 1
        top_units_sorted = sorted(counts_units.items(), key=lambda x: x[1], reverse=True)[:10]
        top_units = [{"unit": k, "count": v} for k, v in top_units_sorted]
    
        return jsonify({
            "total": total,
            "by_day": by_day,
            "by_severity": by_severity,
            "by_source_category": by_source_category,
            "by_status": by_status,
            "top_units": top_units,
        })
    except Exception as e:
        # Return a consistent error payload for frontend handling
        return jsonify({"error": "Failed to compute stats", "details": str(e)}), 500

@app.route('/api/sitreps/delete', methods=['POST'])
def api_sitreps_delete():
    """Delete SITREPs by exact title matches.
    Request JSON: { "titles": ["Title1", "Title2", ...] }
    Returns: { status: "deleted", count: N }
    """
    data = request.json or {}
    titles = data.get('titles') or []
    if not isinstance(titles, list) or not titles:
        return {"error": "Provide a non-empty 'titles' array"}, 400
    # Normalize titles for exact match
    titles = [str(t).strip() for t in titles if str(t).strip()]
    if not titles:
        return {"error": "No valid titles provided"}, 400
    placeholders = ",".join(["?"] * len(titles))
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"DELETE FROM sitreps WHERE title IN ({placeholders})", titles)
    deleted = cur.rowcount if cur.rowcount is not None else 0
    conn.commit()
    conn.close()
    return {"status": "deleted", "count": deleted}

@app.route('/api/sitreps/ai-insights', methods=['GET'])
def api_sitreps_ai_insights():
    """Generate AI insights based on SITREP data patterns and anomalies (Supabase-backed)"""
    try:
        # Build filters compatible with Supabase client
        filters = {}
        range_days = request.args.get('rangeDays')
        if range_days:
            try:
                days = int(range_days)
                cutoff = datetime.utcnow() - timedelta(days=days)
                filters['from_date'] = cutoff.replace(microsecond=0).isoformat() + 'Z'
            except Exception:
                pass

        from_date = request.args.get('fromDate')
        if from_date:
            filters['from_date'] = from_date if 'T' in from_date else f"{from_date}T00:00:00Z"

        to_date = request.args.get('toDate')
        if to_date:
            filters['to_date'] = to_date if 'T' in to_date else f"{to_date}T23:59:59Z"

        sources = request.args.get('sources')
        if sources:
            filters['source_category'] = sources

        # Fetch filtered SITREPs from Supabase
        rows = get_sitreps(filters)

        # Log filtering information
        print(f"AI Insights - Applied filters: {filters}")
        print(f"AI Insights - Processing {len(rows)} filtered records")
        if len(rows) > 0 and rows[0].get('created_at'):
            print(f"AI Insights - Example created_at: {rows[0]['created_at']}")

        # Generate insights via LLM
        insights = generate_sitrep_insights(rows)
        return jsonify(insights)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_sitrep_insights(data):
    """Generate AI insights from SITREP data using OpenRouter"""
    if not data:
        return {
            "patterns": [],
            "anomalies": [],
            "trends": [],
            "summary": "No data available for analysis."
        }

    try:
        # Use OpenRouter for AI analysis
        insights = analyze_with_openrouter(data)
        return insights
    except Exception as e:
        # Fallback to basic analysis if LLM provider is unavailable
        print(f"LLM analysis failed: {e}")
        return {
             "patterns": [{"title": "Basic Analysis", "description": "LLM unavailable, showing basic statistics", "confidence": 50}],
             "anomalies": [],
             "trends": [],
             "summary": f"Basic analysis of {len(data)} incidents. LLM integration unavailable."
         }

def analyze_with_openrouter(data):
    """Analyze SITREP data using OpenRouter LLM only"""
    # Prepare data summary for LLM analysis
    data_summary = prepare_sitrep_data_for_analysis(data)
    prompt = create_sitrep_analysis_prompt(data_summary)

    # Use OpenRouter
    provider = 'openrouter'
    print(f"LLM provider selected for insights: {provider}")
    try:
        llm = create_llm_client(
            provider,
            api_key=app.config.get('OPENROUTER_API_KEY'),
            base_url=app.config.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'),
            model_name=app.config.get('DEFAULT_MODEL')
        )
    except Exception as e:
        raise Exception(f"Failed to initialize LLM client: {e}")

    system_msg = {
        "role": "system",
        "content": "You are an expert military intelligence analyst specializing in SITREP (Situation Report) analysis. Provide detailed, actionable insights in JSON format."
    }
    user_msg = {"role": "user", "content": prompt}

    try:
        ai_response = llm.chat_completion([system_msg, user_msg], temperature=0.3, max_tokens=2000)
        # Treat error-string responses as failures to trigger fallback
        if isinstance(ai_response, str):
            lower = ai_response.lower()
            if lower.startswith('error communicating with lm studio') or lower.startswith('error communicating with openrouter'):
                raise Exception(ai_response)
        # Parse JSON if provided; otherwise attempt text parse
        try:
            insights = json.loads(ai_response)
            return validate_and_format_insights(insights)
        except json.JSONDecodeError:
            return parse_text_response_to_insights(ai_response, data)
    except Exception as e:
        # If LM Studio was selected or client failed, try OpenRouter as fallback
        api_key = app.config.get('OPENROUTER_API_KEY')
        if api_key:
            try:
                fallback_client = create_llm_client(
                    provider='openrouter',
                    api_key=api_key,
                    base_url=app.config.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'),
                    model_name=app.config.get('DEFAULT_MODEL')
                )
                ai_response = fallback_client.chat_completion([system_msg, user_msg], temperature=0.3, max_tokens=2000)
                # Detect error-string from fallback too
                if isinstance(ai_response, str):
                    lower_fb = ai_response.lower()
                    if lower_fb.startswith('error communicating with openrouter'):
                        raise Exception(ai_response)
                try:
                    insights = json.loads(ai_response)
                    return validate_and_format_insights(insights)
                except json.JSONDecodeError:
                    return parse_text_response_to_insights(ai_response, data)
            except Exception as e2:
                raise Exception(f"LLM analysis failed (OpenRouter): {e2}")
        raise Exception(f"LLM analysis failed: {e}")

def prepare_sitrep_data_for_analysis(data):
    """Prepare SITREP data summary for LLM analysis"""
    if not data:
        return "No SITREP data available."
    
    # Create statistical summary
    total_incidents = len(data)
    
    # Severity distribution
    severity_counts = {}
    for item in data:
        severity = item.get('severity', 'Unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Source category distribution
    category_counts = {}
    for item in data:
        category = item.get('source_category', 'Unknown')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Status distribution
    status_counts = {}
    for item in data:
        status = item.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Unit involvement
    unit_counts = {}
    for item in data:
        unit = item.get('unit', 'Unknown')
        if unit and unit != 'Unknown':
            unit_counts[unit] = unit_counts.get(unit, 0) + 1
    
    # Recent incidents (sample)
    recent_incidents = sorted(data, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    incident_samples = []
    for incident in recent_incidents:
        incident_samples.append({
            "severity": incident.get('severity', 'Unknown'),
            "source": incident.get('source', 'Unknown'),
            "category": incident.get('source_category', 'Unknown'),
            "status": incident.get('status', 'Unknown'),
            "unit": incident.get('unit', 'Unknown'),
            "date": incident.get('created_at', 'Unknown')
        })
    
    summary = {
        "total_incidents": total_incidents,
        "severity_distribution": severity_counts,
        "source_categories": category_counts,
        "status_distribution": status_counts,
        "unit_involvement": unit_counts,
        "recent_incident_samples": incident_samples
    }
    
    return json.dumps(summary, indent=2)

def create_sitrep_analysis_prompt(data_summary):
    """Create analysis prompt for LM Studio"""
    prompt = f"""
Analyze the following SITREP (Situation Report) data and provide comprehensive intelligence insights.

SITREP DATA:
{data_summary}

CRITICAL: You must respond with ONLY valid JSON. Do not include any text before or after the JSON. Your entire response must be a valid JSON object.

Provide your analysis in this exact JSON format:
{{
    "patterns": [
        {{
            "title": "Pattern Title",
            "description": "Detailed description of the pattern observed",
            "confidence": 85
        }}
    ],
    "anomalies": [
        {{
            "title": "Anomaly Title", 
            "description": "Description of the anomaly and its implications",
            "severity": "High"
        }}
    ],
    "trends": [
        {{
            "title": "Trend Title",
            "description": "Description of the trend and its trajectory", 
            "direction": "Upward"
        }}
    ],
    "summary": "A comprehensive summary of key findings and recommendations"
}}

Analysis Guidelines:
1. PATTERNS: Identify recurring themes, common characteristics, operational patterns
2. ANOMALIES: Detect unusual events, outliers, unexpected developments (severity: High/Medium/Low)
3. TRENDS: Analyze changes over time, escalation/de-escalation, emerging threats (direction: Upward/Downward/Stable)
4. SUMMARY: Provide key insights, threat assessment, recommended actions

IMPORTANT: Return ONLY the JSON object. No additional text, explanations, or formatting.
"""
    return prompt

def validate_and_format_insights(insights):
    """Validate and format insights from LM Studio response"""
    # Ensure required structure
    formatted = {
        "patterns": insights.get("patterns", []),
        "anomalies": insights.get("anomalies", []),
        "trends": insights.get("trends", []),
        "summary": insights.get("summary", "Analysis completed.")
    }
    
    # Validate patterns
    for pattern in formatted["patterns"]:
        if "confidence" not in pattern:
            pattern["confidence"] = 75
        pattern["confidence"] = min(100, max(0, pattern["confidence"]))
    
    # Validate anomalies
    for anomaly in formatted["anomalies"]:
        if "severity" not in anomaly:
            anomaly["severity"] = "Medium"
        if anomaly["severity"] not in ["High", "Medium", "Low"]:
            anomaly["severity"] = "Medium"
    
    # Validate trends
    for trend in formatted["trends"]:
        if "direction" not in trend:
            trend["direction"] = "Stable"
        if trend["direction"] not in ["Upward", "Downward", "Stable"]:
            trend["direction"] = "Stable"
    
    return formatted

def parse_text_response_to_insights(text_response, data):
    """Parse text response into structured insights if JSON parsing fails"""
    
    # First, try to extract JSON from within the text response
    import re
    
    # Look for JSON blocks in the response (between ``` or just standalone JSON)
    json_patterns = [
        r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
        r'```\s*(\{.*?\})\s*```',      # JSON in generic code blocks
        r'(\{[^{}]*"patterns"[^{}]*\{.*?\}[^{}]*\})',  # JSON with patterns key
        r'(\{.*?"patterns".*?\})',      # Simpler JSON pattern match
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text_response, re.DOTALL | re.IGNORECASE)
        for match in matches:
            try:
                # Clean up the match
                json_str = match.strip()
                # Try to parse as JSON
                parsed_json = json.loads(json_str)
                if isinstance(parsed_json, dict) and any(key in parsed_json for key in ['patterns', 'anomalies', 'trends']):
                    print(f"Successfully extracted JSON from text response")
                    return validate_and_format_insights(parsed_json)
            except json.JSONDecodeError:
                continue
    
    # If no JSON found, try to extract from the beginning of the response
    # Sometimes LLMs return JSON without markdown formatting
    lines = text_response.strip().split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('{'):
            # Try to parse from this line to the end
            potential_json = '\n'.join(lines[i:])
            # Find the matching closing brace
            brace_count = 0
            json_end = 0
            for j, char in enumerate(potential_json):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = j + 1
                        break
            
            if json_end > 0:
                try:
                    json_str = potential_json[:json_end]
                    parsed_json = json.loads(json_str)
                    if isinstance(parsed_json, dict) and any(key in parsed_json for key in ['patterns', 'anomalies', 'trends']):
                        print(f"Successfully extracted JSON from start of response")
                        return validate_and_format_insights(parsed_json)
                except json.JSONDecodeError:
                    continue
    
    # Fallback parsing for non-JSON responses
    insights = {
        "patterns": [],
        "anomalies": [],
        "trends": [],
        "summary": text_response[:500] + "..." if len(text_response) > 500 else text_response
    }
    
    # Try to extract some basic insights from the text
    if "pattern" in text_response.lower():
        insights["patterns"].append({
            "title": "LLM Identified Pattern",
            "description": "Pattern analysis provided by LLM (see summary for details)",
            "confidence": 70
        })
    
    if "anomaly" in text_response.lower() or "unusual" in text_response.lower():
        insights["anomalies"].append({
            "title": "LLM Identified Anomaly",
            "description": "Anomaly detected by LLM (see summary for details)",
            "severity": "Medium"
        })
    
    if "trend" in text_response.lower() or "increasing" in text_response.lower() or "decreasing" in text_response.lower():
        direction = "Upward" if "increasing" in text_response.lower() else "Downward" if "decreasing" in text_response.lower() else "Stable"
        insights["trends"].append({
            "title": "LLM Identified Trend",
            "description": "Trend analysis provided by LLM (see summary for details)",
            "direction": direction
        })
    
    print(f"Using fallback parsing for text response")
    return insights

def analyze_patterns(data):
    """Analyze patterns in SITREP data"""
    patterns = []
    
    if not data:
        return patterns

    # Pattern 1: Severity distribution
    severity_counts = {}
    for item in data:
        severity = item.get('severity', 'Unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    if severity_counts:
        most_common_severity = max(severity_counts, key=severity_counts.get)
        severity_percentage = (severity_counts[most_common_severity] / len(data)) * 100
        
        if severity_percentage > 50:
            patterns.append({
                "title": f"Dominant Severity Level: {most_common_severity}",
                "description": f"{most_common_severity} severity incidents account for {severity_percentage:.1f}% of all reports, indicating a consistent threat level pattern.",
                "confidence": min(95, int(severity_percentage + 20))
            })

    # Pattern 2: Source category clustering
    category_counts = {}
    for item in data:
        category = item.get('source_category', 'Unknown')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    if len(category_counts) > 1:
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        top_category = sorted_categories[0]
        if top_category[1] / len(data) > 0.4:
            patterns.append({
                "title": f"Primary Source Category: {top_category[0]}",
                "description": f"Most incidents ({top_category[1]}/{len(data)}) originate from {top_category[0]} sources, suggesting focused operational areas.",
                "confidence": 85
            })

    # Pattern 3: Unit involvement
    unit_counts = {}
    for item in data:
        unit = item.get('unit', 'Unknown')
        if unit and unit != 'Unknown':
            unit_counts[unit] = unit_counts.get(unit, 0) + 1
    
    if unit_counts:
        most_active_unit = max(unit_counts, key=unit_counts.get)
        unit_percentage = (unit_counts[most_active_unit] / len(data)) * 100
        
        if unit_percentage > 30:
            patterns.append({
                "title": f"High Activity Unit: {most_active_unit}",
                "description": f"Unit {most_active_unit} is involved in {unit_percentage:.1f}% of incidents, indicating high operational tempo or area responsibility.",
                "confidence": 80
            })

    return patterns

def detect_anomalies(data):
    """Detect anomalies in SITREP data"""
    anomalies = []
    
    if len(data) < 5:  # Need sufficient data for anomaly detection
        return anomalies

    # Anomaly 1: Unusual severity spikes
    severity_counts = {}
    for item in data:
        severity = item.get('severity', 'Unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    total_reports = len(data)
    if 'Critical' in severity_counts and severity_counts['Critical'] / total_reports > 0.3:
        anomalies.append({
            "title": "High Critical Incident Rate",
            "description": f"Critical incidents represent {(severity_counts['Critical']/total_reports)*100:.1f}% of reports, which is unusually high and may indicate escalating threats.",
            "severity": "High"
        })

    # Anomaly 2: Geographic clustering (if lat/lon available)
    locations = [(item.get('lat'), item.get('lon')) for item in data if item.get('lat') and item.get('lon')]
    if len(locations) > 3:
        # Simple clustering check - if many incidents in similar coordinates
        lat_variance = sum((lat - sum(l[0] for l in locations)/len(locations))**2 for lat, lon in locations) / len(locations)
        if lat_variance < 0.01:  # Very low variance indicates clustering
            anomalies.append({
                "title": "Geographic Incident Clustering",
                "description": "Multiple incidents are concentrated in a small geographic area, suggesting a localized threat or operational focus.",
                "severity": "Medium"
            })

    # Anomaly 3: Status distribution anomalies
    status_counts = {}
    for item in data:
        status = item.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if 'Open' in status_counts and status_counts['Open'] / total_reports > 0.7:
        anomalies.append({
            "title": "High Open Incident Rate",
            "description": f"{(status_counts['Open']/total_reports)*100:.1f}% of incidents remain open, indicating potential resource constraints or complex situations.",
            "severity": "Medium"
        })

    return anomalies

def analyze_trends(data):
    """Analyze trends in SITREP data"""
    trends = []
    
    if len(data) < 3:
        return trends

    # Sort data by date
    sorted_data = sorted(data, key=lambda x: x.get('created_at', ''))
    
    if len(sorted_data) >= 3:
        # Trend 1: Incident frequency over time
        recent_third = len(sorted_data) // 3
        recent_incidents = sorted_data[-recent_third:] if recent_third > 0 else sorted_data
        older_incidents = sorted_data[:-recent_third] if recent_third > 0 else []
        
        if older_incidents:
            recent_rate = len(recent_incidents)
            older_rate = len(older_incidents) / max(1, len(sorted_data) - recent_third)
            
            if recent_rate > older_rate * 1.5:
                trends.append({
                    "title": "Increasing Incident Frequency",
                    "description": "Recent incident reporting has increased significantly compared to earlier periods, suggesting escalating activity.",
                    "direction": "Upward"
                })
            elif recent_rate < older_rate * 0.7:
                trends.append({
                    "title": "Decreasing Incident Frequency",
                    "description": "Recent incident reporting has decreased compared to earlier periods, indicating potential de-escalation.",
                    "direction": "Downward"
                })

    # Trend 2: Severity evolution
    if len(sorted_data) >= 6:
        first_half = sorted_data[:len(sorted_data)//2]
        second_half = sorted_data[len(sorted_data)//2:]
        
        first_critical = sum(1 for item in first_half if item.get('severity') == 'Critical')
        second_critical = sum(1 for item in second_half if item.get('severity') == 'Critical')
        
        first_rate = first_critical / len(first_half) if first_half else 0
        second_rate = second_critical / len(second_half) if second_half else 0
        
        if second_rate > first_rate * 1.5:
            trends.append({
                "title": "Escalating Threat Severity",
                "description": "The proportion of critical incidents has increased over time, indicating escalating threat levels.",
                "direction": "Upward"
            })

    return trends

def generate_summary(data, patterns, anomalies, trends):
    """Generate a summary of insights"""
    total_incidents = len(data)
    
    if total_incidents == 0:
        return "No incidents to analyze."
    
    summary_parts = [
        f"Analysis of {total_incidents} incident reports reveals:"
    ]
    
    if patterns:
        summary_parts.append(f"{len(patterns)} significant patterns identified")
    
    if anomalies:
        summary_parts.append(f"{len(anomalies)} anomalies detected")
    
    if trends:
        summary_parts.append(f"{len(trends)} trends observed")
    
    # Add key insights
    severity_counts = {}
    for item in data:
        severity = item.get('severity', 'Unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    if severity_counts:
        most_common = max(severity_counts, key=severity_counts.get)
        summary_parts.append(f"Most common severity level is {most_common}")
    
    if not patterns and not anomalies and not trends:
        summary_parts.append("The data shows normal operational patterns with no significant anomalies detected.")
    
    return ". ".join(summary_parts) + "."

# Chatbot API endpoints
@app.route('/api/chatbot/query', methods=['POST'])
def api_chatbot_query():
    """Handle chatbot queries about SITREP data"""
    try:
        data = request.json or {}
        user_query = data.get('query', '').strip()
        session_id = data.get('session_id')  # Optional session ID
        
        if not user_query:
            return {"error": "Query is required"}, 400
        
        # Process query through chatbot with session support
        response = chatbot.process_query(user_query, session_id=session_id)
        
        return jsonify({
            "status": "success",
            "response": response
        })
    
    except Exception as e:
        return {"error": f"Chatbot error: {str(e)}"}, 500

@app.route('/api/chatbot/models', methods=['GET'])
def api_chatbot_models():
    """Get available OpenRouter models"""
    try:
        # Guard against uninitialized LLM
        if getattr(chatbot, 'llm', None) is None:
            return jsonify({
                "status": "success",
                "models": []
            })
        models = chatbot.llm.get_available_models()
        return jsonify({
            "status": "success",
            "models": models
        })
    except Exception as e:
        return {"error": f"Error fetching models: {str(e)}"}, 500

@app.route('/api/chatbot/config', methods=['GET', 'POST'])
def api_chatbot_config():
    """Get or update chatbot configuration"""
    if request.method == 'GET':
        # Safely provide config even if LLM is not initialized
        lm_url = getattr(getattr(chatbot, 'llm', None), 'base_url', app.config.get('OPENROUTER_BASE_URL') or '')
        model_name = getattr(getattr(chatbot, 'llm', None), 'model_name', app.config.get('DEFAULT_MODEL') or '')
        return jsonify({
            "status": "success",
            "config": {
                "lm_studio_url": lm_url,
                "model_name": model_name
            }
        })
    else:
        try:
            data = request.json or {}
            # Update LM Studio URL if provided
            if 'lm_studio_url' in data:
                if getattr(chatbot, 'llm', None) is not None:
                    chatbot.llm.base_url = data['lm_studio_url'].rstrip('/')
                else:
                    app.config['OPENROUTER_BASE_URL'] = data['lm_studio_url'].rstrip('/')
            # Update model name if provided
            if 'model_name' in data:
                if getattr(chatbot, 'llm', None) is not None:
                    chatbot.llm.model_name = data['model_name']
                else:
                    app.config['DEFAULT_MODEL'] = data['model_name']
            return jsonify({
                "status": "success",
                "message": "Configuration updated"
            })
        except Exception as e:
            return {"error": f"Configuration error: {str(e)}"}, 500

@app.route('/api/health/supabase', methods=['GET'])
def api_health_supabase():
    """Health check to verify Supabase connectivity"""
    try:
        data = get_sitreps()
        return jsonify({
            "status": "ok",
            "count": len(data) if data else 0
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/health/openrouter', methods=['GET'])
def api_openrouter_health():
    """Check OpenRouter connectivity and model access"""
    base_url = app.config.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    model = app.config.get('DEFAULT_MODEL')
    api_key = app.config.get('OPENROUTER_API_KEY')
    result = {
        'base_url': base_url,
        'model': model,
        'api_key_present': bool(api_key)
    }
    try:
        llm = create_llm_client(
            'openrouter',
            api_key=api_key,
            base_url=base_url,
            model_name=model
        )
        # Check models list
        models = llm.get_available_models()
        result['models_count'] = len(models)
        result['models_sample'] = models[:5] if isinstance(models, list) else []
        # Check minimal chat completion
        messages = [
            {"role": "system", "content": "Reply only with the word 'pong'."},
            {"role": "user", "content": "ping"}
        ]
        resp = llm.chat_completion(messages, temperature=0.0, max_tokens=5)
        ok = isinstance(resp, str) and not resp.lower().startswith('error communicating with openrouter')
        result['chat_ok'] = ok
        result['chat_response'] = resp if isinstance(resp, str) else str(resp)
        return jsonify({"status": "success", "openrouter": result})
    except Exception as e:
        result['error'] = str(e)
        return jsonify({"status": "error", "openrouter": result}), 500

@app.route('/api/random-question', methods=['GET'])
def api_random_question():
    """Get a random question from UN_Dignitary_Questions.txt"""
    try:
        import random
        
        # Path to the questions file
        questions_file = os.path.join(os.path.dirname(__file__), "UN_Dignitary_Questions.txt")
        
        if not os.path.exists(questions_file):
            return {"error": "Questions file not found"}, 404
        
        # Read the file and extract questions
        with open(questions_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract numbered questions (lines that start with a number followed by a period)
        lines = content.split('\n')
        questions = []
        
        for line in lines:
            line = line.strip()
            # Look for lines that start with a number followed by a period
            if line and len(line) > 3 and line[0].isdigit() and '. ' in line[:5]:
                # Extract the question part (everything after the number and period)
                question_text = line.split('. ', 1)[1] if '. ' in line else line
                questions.append(question_text)
        
        if not questions:
            return {"error": "No questions found in file"}, 404
        
        # Return a random question
        random_question = random.choice(questions)
        
        return jsonify({
            "status": "success",
            "question": random_question,
            "total_questions": len(questions)
        })
        
    except Exception as e:
        return {"error": f"Error fetching random question: {str(e)}"}, 500

# SocketIO event handlers for streaming
@socketio.on('chatbot_query_stream')
def handle_chatbot_query_stream(data):
    """Handle streaming chatbot queries via SocketIO"""
    try:
        user_query = data.get('query', '').strip()
        session_id = data.get('session_id')  # Optional session ID
        
        if not user_query:
            emit('chatbot_error', {'error': 'Query is required'})
            return
        
        # Process query through chatbot with streaming and session support
        response = chatbot.process_query_stream(user_query, emit_callback=emit, session_id=session_id)
        
        # Emit completion with final response
        emit('chatbot_stream_complete', {'response': response})
        
    except Exception as e:
        emit('chatbot_error', {'error': f'Chatbot error: {str(e)}'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected to chatbot streaming')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected from chatbot streaming')

if __name__ == '__main__':
    # Validate production config if in production
    if app.config.get('FLASK_ENV') == 'production':
        try:
            from config import ProductionConfig
            ProductionConfig.validate_production_config()
        except ValueError as e:
            print(f"Production configuration error: {e}")
            exit(1)
    
    # Railway deployment configuration
    # Railway provides PORT environment variable and expects binding to 0.0.0.0
    port = int(os.environ.get('PORT', app.config['PORT']))
    host = os.environ.get('HOST', '0.0.0.0')  # Always bind to 0.0.0.0 for Railway
    
    print(f"Starting server on {host}:{port}")
    print(f"Debug mode: {app.config['DEBUG']}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    socketio.run(
        app, 
        debug=app.config['DEBUG'],
        host=host,
        port=port,
        allow_unsafe_werkzeug=True  # Required for Railway deployment
    )
