"""
Supabase client module for database operations and storage
"""
import os
import json
from supabase import create_client, Client
from storage3.utils import StorageException

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance (for read operations)
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
    
    return create_client(url, key)

def get_admin_supabase_client() -> Client:
    """
    Create and return a Supabase client with service role key (for write operations)
    """
    url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not service_key:
        # Fall back to anonymous client if service key not available
        return get_supabase_client()
    
    return create_client(url, service_key)

def get_storage_client():
    """
    Get the storage client from Supabase (for read operations)
    """
    supabase = get_supabase_client()
    return supabase.storage

def get_admin_storage_client():
    """
    Get the storage client with admin privileges (for write operations)
    """
    supabase = get_admin_supabase_client()
    return supabase.storage

def get_sitreps(filters=None):
    """
    Get sitreps from Supabase with optional filters
    """
    supabase = get_supabase_client()
    query = supabase.table("sitreps").select("*")
    
    # Apply filters if provided
    if filters:
        if filters.get("from_date"):
            # Use created_at for temporal filtering
            query = query.gte("created_at", filters["from_date"])
        if filters.get("to_date"):
            query = query.lte("created_at", filters["to_date"])
        if filters.get("source_category"):
            categories = filters["source_category"].split(",")
            query = query.in_("source_category", categories)
    
    # Order by created_at descending (fallback to id if column missing)
    try:
        query = query.order("created_at", desc=True)
    except Exception:
        query = query.order("id", desc=True)
    
    response = query.execute()
    return response.data

def insert_sitrep(sitrep_data):
    """
    Insert a new sitrep into Supabase
    """
    supabase = get_supabase_client()
    response = supabase.table("sitreps").insert(sitrep_data).execute()
    
    if response.data:
        return {"status": "success", "id": response.data[0]["id"]}
    else:
        return {"status": "error", "message": "Failed to insert sitrep"}

def get_sitrep_by_id(sitrep_id):
    """
    Get a single sitrep by ID
    """
    supabase = get_supabase_client()
    response = supabase.table("sitreps").select("*").eq("id", sitrep_id).execute()
    
    if response.data:
        return response.data[0]
    return None

def update_sitrep(sitrep_id, update_data):
    """
    Update an existing sitrep
    """
    supabase = get_supabase_client()
    response = supabase.table("sitreps").update(update_data).eq("id", sitrep_id).execute()
    
    if response.data:
        return {"status": "success", "id": sitrep_id}
    else:
        return {"status": "error", "message": "Failed to update sitrep"}

def delete_sitrep(sitrep_id):
    """
    Delete a sitrep by ID
    """
    supabase = get_supabase_client()
    response = supabase.table("sitreps").delete().eq("id", sitrep_id).execute()
    return response.data

# Layer Storage Functions
LAYERS_BUCKET = "Geojson"

def ensure_layers_bucket():
    """
    Ensure the layers bucket exists. 
    Note: This function no longer creates buckets automatically.
    Bucket creation requires elevated permissions and should be done manually.
    
    Returns:
        bool: True if bucket exists, False otherwise
    """
    try:
        storage = get_storage_client()
        
        # Try to get bucket info
        bucket_info = storage.get_bucket(LAYERS_BUCKET)
        return True
    except Exception as e:
        # If bucket metadata access fails, try listing files as a fallback
        # This handles cases where the bucket exists but metadata access is restricted
        try:
            storage.from_(LAYERS_BUCKET).list()
            print(f"✅ Bucket '{LAYERS_BUCKET}' is accessible (metadata access restricted)")
            return True
        except Exception as list_error:
            print(f"Bucket '{LAYERS_BUCKET}' not found. Please create it manually in Supabase dashboard.")
            print(f"Error: {e}")
            print("See SUPABASE_BUCKET_SETUP.md for detailed setup instructions.")
            return False

def upload_layer_to_bucket(layer_name, geojson_data):
    """
    Upload a layer (GeoJSON) to Supabase storage bucket
    
    Args:
        layer_name (str): Name of the layer
        geojson_data (dict): GeoJSON data to upload
    
    Returns:
        dict: Upload response or error
    """
    try:
        # Use admin storage client for write operations
        storage = get_admin_storage_client()
        
        # Ensure bucket exists
        if not ensure_layers_bucket():
            return {"error": "Failed to ensure bucket exists"}
        
        # Convert GeoJSON to string
        geojson_str = json.dumps(geojson_data, ensure_ascii=False, indent=2)
        geojson_bytes = geojson_str.encode('utf-8')
        
        # Upload file
        file_path = f"{layer_name}.geojson"
        response = storage.from_(LAYERS_BUCKET).upload(
            file_path, 
            geojson_bytes,
            {"content-type": "application/json"}
        )
        
        return {"success": True, "path": response.path}
    except StorageException as e:
        # If file exists, update it instead
        if "already exists" in str(e).lower():
            return update_layer_in_bucket(layer_name, geojson_data)
        return {"error": f"Storage error: {str(e)}"}
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}

def update_layer_in_bucket(layer_name, geojson_data):
    """
    Update an existing layer in the bucket
    
    Args:
        layer_name (str): Name of the layer
        geojson_data (dict): Updated GeoJSON data
    
    Returns:
        dict: Update response or error
    """
    try:
        # Use admin storage client for write operations
        storage = get_admin_storage_client()
        
        # Convert GeoJSON to string
        geojson_str = json.dumps(geojson_data, ensure_ascii=False, indent=2)
        geojson_bytes = geojson_str.encode('utf-8')
        
        # Update file
        file_path = f"{layer_name}.geojson"
        response = storage.from_(LAYERS_BUCKET).update(
            file_path, 
            geojson_bytes,
            {"content-type": "application/json"}
        )
        
        return {"success": True, "path": response.path}
    except Exception as e:
        return {"error": f"Update failed: {str(e)}"}

def download_layer_from_bucket(layer_name):
    """
    Download a layer from Supabase storage bucket
    
    Args:
        layer_name (str): Name of the layer
    
    Returns:
        dict: GeoJSON data or error
    """
    try:
        storage = get_storage_client()
        
        file_path = f"{layer_name}.geojson"
        response = storage.from_(LAYERS_BUCKET).download(file_path)
        
        # Parse the downloaded bytes as JSON
        geojson_data = json.loads(response.decode('utf-8'))
        return {"success": True, "data": geojson_data}
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}

def list_layers_in_bucket():
    """
    List all layers in the bucket
    
    Returns:
        list: List of layer names or error
    """
    try:
        storage = get_storage_client()
        
        response = storage.from_(LAYERS_BUCKET).list()
        
        # Extract layer names (remove .geojson extension)
        layer_names = []
        for file_info in response:
            if file_info.get("name", "").endswith(".geojson"):
                layer_name = file_info["name"][:-8]  # Remove .geojson
                layer_names.append(layer_name)
        
        return {"success": True, "layers": layer_names}
    except Exception as e:
        return {"error": f"List failed: {str(e)}"}

def delete_layer_from_bucket(layer_name):
    """
    Delete a layer from the bucket
    
    Args:
        layer_name (str): Name of the layer to delete
    
    Returns:
        dict: Success or error response
    """
    try:
        # Use admin storage client for write operations
        storage = get_admin_storage_client()
        
        file_path = f"{layer_name}.geojson"
        response = storage.from_(LAYERS_BUCKET).remove([file_path])
        
        return {"success": True, "message": f"Layer {layer_name} deleted"}
    except Exception as e:
        return {"error": f"Delete failed: {str(e)}"}

# Conversation management functions
def get_conversation_history(session_id, limit=10):
    """
    Get conversation history for a session
    """
    supabase = get_supabase_client()
    response = supabase.table("chatbot_conversations").select("*").eq("session_id", session_id).order("timestamp", desc=True).limit(limit).execute()
    
    # Return in chronological order (oldest first)
    return list(reversed(response.data)) if response.data else []

def save_conversation_message(session_id, user_message, bot_response, context_data=None):
    """
    Save a conversation message to the database
    """
    supabase = get_supabase_client()
    conversation_data = {
        "session_id": session_id,
        "user_message": user_message,
        "bot_response": bot_response,
        "context_data": context_data
    }
    
    response = supabase.table("chatbot_conversations").insert(conversation_data).execute()
    
    if response.data:
        return {"status": "success", "id": response.data[0]["id"]}
    else:
        return {"status": "error", "message": "Failed to save conversation"}

def get_recent_conversations(session_id, count=5):
    """
    Get recent conversation messages for context
    """
    supabase = get_supabase_client()
    response = supabase.table("chatbot_conversations").select("user_message, bot_response").eq("session_id", session_id).order("timestamp", desc=True).limit(count).execute()
    
    # Return in chronological order (oldest first)
    return list(reversed(response.data)) if response.data else []

def clear_conversation_history(session_id):
    """
    Clear conversation history for a session
    """
    supabase = get_supabase_client()
    response = supabase.table("chatbot_conversations").delete().eq("session_id", session_id).execute()
    
    return {"status": "success", "deleted_count": len(response.data) if response.data else 0}

# Authentication functions
def authenticate_user(username, password):
    """
    Authenticate user with username and password
    Returns user data if successful, None if failed
    """
    try:
        supabase = get_admin_supabase_client()  # Use admin client for authentication
        response = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            # Don't return password in user data
            user.pop('password', None)
            return user
        return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def create_user(username, password, email=None, role="user"):
    """
    Create a new user in the database
    """
    try:
        supabase = get_admin_supabase_client()
        user_data = {
            "username": username,
            "password": password,  # In production, this should be hashed
            "email": email,
            "role": role,
            "created_at": "now()"
        }
        response = supabase.table("users").insert(user_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"User creation error: {e}")
        return None

def get_user_by_username(username):
    """
    Get user by username
    """
    try:
        supabase = get_admin_supabase_client()  # Use admin client for user lookup
        response = supabase.table("users").select("*").eq("username", username).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            # Don't return password in user data
            user.pop('password', None)
            return user
        return None
    except Exception as e:
        print(f"Get user error: {e}")
        return None