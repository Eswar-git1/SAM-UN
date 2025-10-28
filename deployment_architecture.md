# Free Hosting Architecture Plan

## Current vs Proposed Architecture

### Current (Local)
```
Flask App (app.py) → SQLite → LM Studio (localhost:1234) → Local Tile Server
```

### Proposed (Free Cloud)
```
Vercel (Frontend) ↔ Railway (Flask API) ↔ Supabase (PostgreSQL) ↔ OpenRouter (LLM)
                                        ↔ OpenStreetMap/Mapbox (Tiles)
```

## Component Breakdown

### 1. **Railway (Backend API)**
- Host the Flask application as an API server
- Handle all backend logic, database operations
- Serve WebSocket connections for real-time features
- Process file uploads and geospatial operations

### 2. **Vercel (Frontend)**
- Serve static HTML, CSS, JavaScript files
- Handle client-side map rendering
- Communicate with Railway backend via API calls

### 3. **Supabase (Database)**
- PostgreSQL with PostGIS extension for spatial data
- Real-time subscriptions for live updates
- Built-in authentication if needed

### 4. **OpenRouter (LLM)**
- Replace LM Studio with cloud-based inference
- Support for multiple models (GPT-3.5, Claude, etc.)
- Pay-per-use pricing after free credits

### 5. **Public Tile Services**
- OpenStreetMap: Free, no limits
- Mapbox: Free tier (50k loads/month)

## Migration Steps

1. **Separate Frontend/Backend**
   - Extract HTML templates to static files
   - Convert Flask routes to API endpoints
   - Update frontend to use fetch/AJAX calls

2. **Database Migration**
   - Export SQLite data
   - Set up Supabase PostgreSQL
   - Create migration scripts

3. **LLM Integration**
   - Replace LM Studio client with OpenRouter
   - Update API endpoints and configuration

4. **Deployment Configuration**
   - Create Railway deployment files
   - Set up Vercel configuration
   - Configure environment variables

## Cost Estimation (Monthly)
- **Vercel**: Free (within limits)
- **Railway**: $5 credit (usually sufficient)
- **Supabase**: Free (500MB database)
- **OpenRouter**: ~$5-10 (depending on usage)
- **Mapbox**: Free (50k loads)

**Total**: ~$5-15/month (mostly LLM usage)