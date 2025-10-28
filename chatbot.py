"""
Chatbot module for SITREP database queries using OpenRouter LLM
"""
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import uuid
from llm_client import create_llm_client, LLMClient
from supabase_client import get_sitreps, get_sitrep_by_id, get_recent_conversations, save_conversation_message

class SitrepDatabase:
    """Helper class for querying SITREP database"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        # db_path is kept for compatibility but not used with Supabase
    
    def get_all_sitreps(self, limit: int = 100) -> List[Dict]:
        """Get all SITREPs with optional limit"""
        # Use Supabase client to get sitreps
        sitreps = get_sitreps()
        # Apply limit in Python since Supabase client doesn't support it directly
        return sitreps[:limit] if sitreps else []
    
    def get_sitreps_by_severity(self, severity: str) -> List[Dict]:
        """Get SITREPs by severity level"""
        # Use Supabase client to get sitreps and filter by severity
        sitreps = get_sitreps()
        # Filter in Python since we're not implementing custom filters in the client
        return [s for s in sitreps if s.get('severity', '').lower() == severity.lower()]
    
    def get_sitreps_by_status(self, status: str) -> List[Dict]:
        """Get SITREPs by status"""
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, source, source_category, incident_type, title, description, 
                   severity, status, unit, contact, lat, lon, created_at 
            FROM sitreps 
            WHERE LOWER(status) = LOWER(?)
            ORDER BY created_at DESC
        """, (status,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    
    def get_sitreps_by_incident_type(self, incident_type: str) -> List[Dict]:
        """Get SITREPs by incident type"""
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, source, source_category, incident_type, title, description, 
                   severity, status, unit, contact, lat, lon, created_at 
            FROM sitreps 
            WHERE LOWER(incident_type) = LOWER(?)
            ORDER BY created_at DESC
        """, (incident_type,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    
    def get_recent_sitreps(self, hours: int = 24) -> List[Dict]:
        """Get SITREPs from the last N hours"""
        # Use Supabase client to get all sitreps
        sitreps = get_sitreps()
        
        # Filter by time in Python
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Since we may not have timestamp data, return all sitreps for now
        # In a real implementation, we would filter: 
        # return [s for s in sitreps if s.get('timestamp') and datetime.fromisoformat(s.get('timestamp')) >= cutoff_time]
        return sitreps[:10]  # Return first 10 as a sample
    
    def get_sitreps_by_location(self, lat: float, lon: float, radius_km: float = 10) -> List[Dict]:
        """Get SITREPs within a certain radius of a location"""
        conn = self.get_connection()
        cur = conn.cursor()
        # Simple distance calculation (not precise for large distances)
        cur.execute("""
            SELECT id, source, source_category, incident_type, title, description, 
                   severity, status, unit, contact, lat, lon, created_at,
                   (6371 * acos(cos(radians(?)) * cos(radians(lat)) * 
                   cos(radians(lon) - radians(?)) + sin(radians(?)) * 
                   sin(radians(lat)))) AS distance
            FROM sitreps 
            HAVING distance < ?
            ORDER BY distance ASC
        """, (lat, lon, lat, radius_km))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        # Total count
        cur.execute("SELECT COUNT(*) as total FROM sitreps")
        total = cur.fetchone()['total']
        
        # By severity
        cur.execute("""
            SELECT severity, COUNT(*) as count 
            FROM sitreps 
            GROUP BY severity 
            ORDER BY count DESC
        """)
        by_severity = [dict(r) for r in cur.fetchall()]
        
        # By status
        cur.execute("""
            SELECT status, COUNT(*) as count 
            FROM sitreps 
            WHERE status IS NOT NULL AND status != ''
            GROUP BY status 
            ORDER BY count DESC
        """)
        by_status = [dict(r) for r in cur.fetchall()]
        
        # By incident type
        cur.execute("""
            SELECT incident_type, COUNT(*) as count 
            FROM sitreps 
            WHERE incident_type IS NOT NULL AND incident_type != ''
            GROUP BY incident_type 
            ORDER BY count DESC
        """)
        by_incident_type = [dict(r) for r in cur.fetchall()]
        
        # Recent activity (last 24 hours)
        cur.execute("""
            SELECT COUNT(*) as recent_count 
            FROM sitreps 
            WHERE datetime(created_at) >= datetime('now', '-24 hours')
        """)
        recent_count = cur.fetchone()['recent_count']
        
        conn.close()
        
        return {
            'total_sitreps': total,
            'recent_24h': recent_count,
            'by_severity': by_severity,
            'by_status': by_status,
            'by_incident_type': by_incident_type
        }





class SitrepChatbot:
    """Main chatbot class that combines database queries with LLM responses"""
    
    def __init__(self, db_path: str = None, llm_provider: str = "openrouter", llm_config: dict = None):
        self.db = SitrepDatabase(db_path) if db_path else SitrepDatabase()
        
        if llm_config is None:
            llm_config = {}
        
        # Initialize LLM if client is provided via config
        client = llm_config.get('client') if isinstance(llm_config, dict) else None
        if client and isinstance(client, LLMClient):
            self.llm = client
        else:
            # Fallback: leave uninitialized; server will attempt to configure
            self.llm = None
        
    def process_query(self, user_query: str, session_id: str = None) -> Dict[str, Any]:
        """Process user query and return response with data and LLM analysis"""
        from supabase_client import get_sitreps
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        sitreps = get_sitreps()
        
        response = {
            "data": sitreps,
            "query": user_query,
            "message": f"Found {len(sitreps)} sitreps",
            "session_id": session_id
        }
        
        # If LLM is available, augment with LLM analysis of recent data
        if self.llm:
            try:
                llm_text = self._generate_llm_response_with_context(
                    user_query,
                    sitreps[:20] if sitreps else [],
                    "recent SITREPs from the database",
                    session_id
                )
                response["llm_response"] = llm_text
                
                # Save conversation to database
                try:
                    save_conversation_message(session_id, user_query, llm_text, json.dumps({"data_count": len(sitreps)}))
                except Exception as e:
                    print(f"Warning: Failed to save conversation: {e}")
                    
            except Exception as e:
                response["llm_response"] = f"LLM error: {str(e)}"
        
        return response
        
    def _generate_llm_response(self, user_query: str, data: List[Dict], context: str) -> str:
        """Generate LLM response based on query and data"""
        if not self.llm:
            return "LLM not configured. Please set up OpenRouter API key to enable AI responses."
        
        data_summary = self._prepare_data_summary(data)
        system_prompt = """You are a helpful assistant analyzing SITREP (Situation Report) data for military/emergency operations. 
        Your role is to analyze provided SITREP data, answer questions clearly, highlight patterns/trends, and provide actionable insights. Be factual and base responses on the provided data."""
        user_prompt = f"""
        User Question: {user_query}
        Context: I'm providing you with {context}.
        SITREP Data:
        {data_summary}
        Please analyze this data and provide a helpful response to the user's question.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return self.llm.chat_completion(messages)
    
    def _generate_llm_response_with_context(self, user_query: str, data: List[Dict], context: str, session_id: str) -> str:
        """Generate LLM response based on query, data, and conversation history"""
        if not self.llm:
            return "LLM not configured. Please set up OpenRouter API key to enable AI responses."
        
        # Get recent conversation history for context
        conversation_history = get_recent_conversations(session_id, count=5)
        
        data_summary = self._prepare_data_summary(data)
        system_prompt = """You are a helpful assistant analyzing SITREP (Situation Report) data for military/emergency operations. 
        Your role is to analyze provided SITREP data, answer questions clearly, highlight patterns/trends, and provide actionable insights. Be factual and base responses on the provided data.
        
        You have access to the conversation history to maintain context and provide more relevant responses. Reference previous exchanges when appropriate."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history to messages
        for conv in conversation_history:
            messages.append({"role": "user", "content": conv["user_message"]})
            messages.append({"role": "assistant", "content": conv["bot_response"]})
        
        # Add current query with data context
        user_prompt = f"""
        User Question: {user_query}
        Context: I'm providing you with {context}.
        SITREP Data:
        {data_summary}
        Please analyze this data and provide a helpful response to the user's question. Consider our previous conversation for context.
        """
        messages.append({"role": "user", "content": user_prompt})
        
        return self.llm.chat_completion(messages)
        
    def _generate_stats_response(self, user_query: str, stats: Dict) -> Dict[str, Any]:
        """Generate response for statistics queries"""
        if not self.llm:
            return {
                'user_query': user_query,
                'data_context': 'database statistics',
                'relevant_data': stats,
                'llm_response': 'LLM not configured. Statistics computed without AI analysis.',
                'data_count': stats.get('total_sitreps', 0)
            }
        
        system_prompt = "You are analyzing SITREP database statistics. Provide a clear, informative summary of the data patterns and key insights."
        user_prompt = f"""
        User Question: {user_query}
        Database Statistics:
        - Total SITREPs: {stats['total_sitreps']}
        - Recent (24h): {stats['recent_24h']}
        - By Severity: {json.dumps(stats['by_severity'], indent=2)}
        - By Status: {json.dumps(stats['by_status'], indent=2)}
        - By Incident Type: {json.dumps(stats['by_incident_type'], indent=2)}
        Please provide an analysis of these statistics.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        llm_response = self.llm.chat_completion(messages)
        return {
            'user_query': user_query,
            'data_context': 'database statistics',
            'relevant_data': stats,
            'llm_response': llm_response,
            'data_count': stats['total_sitreps']
        }
        
    def _prepare_data_summary(self, data: List[Dict]) -> str:
        """Prepare a concise summary of SITREP data for LLM"""
        if not data:
            return "No relevant SITREPs found."
        
        summary_lines = []
        for i, sitrep in enumerate(data, 1):
            line = f"{i}. [{sitrep.get('severity', 'Unknown')}] {sitrep.get('title', 'No title')}"
            if sitrep.get('description'):
                line += f" - {sitrep['description'][:100]}{'...' if len(sitrep.get('description', '')) > 100 else ''}"
            if sitrep.get('status'):
                line += f" (Status: {sitrep['status']})"
            if sitrep.get('created_at'):
                line += f" (Created: {sitrep['created_at']})"
            summary_lines.append(line)
        
        return "\n".join(summary_lines)
    
    def _extract_coordinates(self, data: List[Dict]) -> List[Dict]:
        """Extract valid coordinates from SITREP data for mapping"""
        coordinates = []
        
        for sitrep in data:
            lat = sitrep.get('lat')
            lon = sitrep.get('lon')
            
            # Check if coordinates are valid (not None, not empty, and numeric)
            if lat is not None and lon is not None:
                try:
                    lat_float = float(lat)
                    lon_float = float(lon)
                    
                    # Basic validation for reasonable coordinate ranges
                    if -90 <= lat_float <= 90 and -180 <= lon_float <= 180:
                        coordinates.append({
                            'id': sitrep.get('id'),
                            'lat': lat_float,
                            'lon': lon_float,
                            'title': sitrep.get('title', 'Unknown'),
                            'severity': sitrep.get('severity', 'Unknown'),
                            'status': sitrep.get('status', 'Unknown'),
                            'incident_type': sitrep.get('incident_type', 'Unknown'),
                            'description': sitrep.get('description', ''),
                            'created_at': sitrep.get('created_at', ''),
                            'unit': sitrep.get('unit', ''),
                            'contact': sitrep.get('contact', '')
                        })
                except (ValueError, TypeError):
                    # Skip invalid coordinates
                    continue
        
        return coordinates
    
    def _is_mapping_query(self, user_query: str) -> bool:
        """Determine if the user query is asking for location/mapping information"""
        query_lower = user_query.lower()
        
        mapping_keywords = [
            'map', 'location', 'where', 'coordinates', 'lat', 'lon', 'latitude', 'longitude',
            'plot', 'show on map', 'geographic', 'position', 'place', 'area', 'region',
            'near', 'around', 'vicinity', 'distance', 'route', 'direction'
        ]
        
        return any(keyword in query_lower for keyword in mapping_keywords)
    
    def process_query_stream(self, user_query: str, emit_callback=None, session_id: str = None) -> Dict[str, Any]:
        """Process user query with streaming LLM response"""
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            
        query_lower = user_query.lower()
        relevant_data = []
        if emit_callback:
            emit_callback('chatbot_stream_status', {'status': 'Fetching relevant data...'})
        
        if any(word in query_lower for word in ['recent', 'latest', 'new', 'today']):
            relevant_data = self.db.get_recent_sitreps(24)
            data_context = "recent SITREPs from the last 24 hours"
        elif any(word in query_lower for word in ['critical', 'high', 'urgent']):
            relevant_data = self.db.get_sitreps_by_severity('Critical') + self.db.get_sitreps_by_severity('High')
            data_context = "high and critical severity SITREPs"
        elif any(word in query_lower for word in ['ongoing', 'active']):
            relevant_data = self.db.get_sitreps_by_status('ongoing')
            data_context = "ongoing SITREPs"
        elif any(word in query_lower for word in ['resolved', 'completed', 'closed']):
            relevant_data = self.db.get_sitreps_by_status('resolved')
            data_context = "resolved SITREPs"
        elif any(word in query_lower for word in ['statistics', 'stats', 'summary', 'overview']):
            stats = self.db.get_statistics()
            return self._generate_stats_response_stream(user_query, stats, emit_callback)
        else:
            relevant_data = self.db.get_recent_sitreps(720)
            data_context = "recent SITREPs from the last 30 days"
        
        if len(relevant_data) > 20:
            relevant_data = relevant_data[:20]
        coordinates = self._extract_coordinates(relevant_data)
        is_mapping_query = self._is_mapping_query(user_query)
        
        if emit_callback:
            emit_callback('chatbot_stream_status', {'status': 'Analyzing data and generating response...'})
        
        if not self.llm:
            # Fallback: non-streaming response
            fallback_text = "LLM not configured. Showing recent SITREPs summary without AI analysis."
            return {
                'user_query': user_query,
                'data_context': data_context,
                'relevant_data': relevant_data,
                'llm_response': fallback_text,
                'data_count': len(relevant_data),
                'coordinates': coordinates,
                'has_coordinates': len(coordinates) > 0,
                'is_mapping_query': is_mapping_query
            }
        
        llm_response = self._generate_llm_response_stream_with_context(user_query, relevant_data, data_context, session_id, emit_callback)
        
        # Save conversation to database
        try:
            save_conversation_message(session_id, user_query, llm_response, json.dumps({
                "data_count": len(relevant_data),
                "data_context": data_context,
                "has_coordinates": len(coordinates) > 0,
                "is_mapping_query": is_mapping_query
            }))
        except Exception as e:
            print(f"Warning: Failed to save conversation: {e}")
        
        return {
            'user_query': user_query,
            'data_context': data_context,
            'relevant_data': relevant_data,
            'llm_response': llm_response,
            'data_count': len(relevant_data),
            'coordinates': coordinates,
            'has_coordinates': len(coordinates) > 0,
            'is_mapping_query': is_mapping_query,
            'session_id': session_id
        }
        
    def _generate_llm_response_stream(self, user_query: str, data: List[Dict], context: str, emit_callback=None) -> str:
        """Generate streaming LLM response based on query and data"""
        if not self.llm:
            return "LLM not configured."
        data_summary = self._prepare_data_summary(data)
        system_prompt = """You are a helpful assistant analyzing SITREP (Situation Report) data for military/emergency operations. 
        Your role is to analyze provided SITREP data, answer questions clearly, highlight patterns/trends, and provide actionable insights. Be factual and base responses on the provided data."""
        user_prompt = f"""
        User Question: {user_query}
        Context: I'm providing you with {context}.
        SITREP Data:
        {data_summary}
        Please analyze this data and provide a helpful response to the user's question.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return self.llm.chat_completion_stream(messages, callback=emit_callback)
    
    def _generate_llm_response_stream_with_context(self, user_query: str, data: List[Dict], context: str, session_id: str, emit_callback=None) -> str:
        """Generate streaming LLM response based on query, data, and conversation history"""
        if not self.llm:
            return "LLM not configured."
        
        # Get recent conversation history for context
        conversation_history = get_recent_conversations(session_id, count=5)
        
        data_summary = self._prepare_data_summary(data)
        system_prompt = """You are a helpful assistant analyzing SITREP (Situation Report) data for military/emergency operations. 
        Your role is to analyze provided SITREP data, answer questions clearly, highlight patterns/trends, and provide actionable insights. Be factual and base responses on the provided data.
        
        You have access to the conversation history to maintain context and provide more relevant responses. Reference previous exchanges when appropriate."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history to messages
        for conv in conversation_history:
            messages.append({"role": "user", "content": conv["user_message"]})
            messages.append({"role": "assistant", "content": conv["bot_response"]})
        
        # Add current query with data context
        user_prompt = f"""
        User Question: {user_query}
        Context: I'm providing you with {context}.
        SITREP Data:
        {data_summary}
        Please analyze this data and provide a helpful response to the user's question. Consider our previous conversation for context.
        """
        messages.append({"role": "user", "content": user_prompt})
        
        return self.llm.chat_completion_stream(messages, callback=emit_callback)
        
    def _generate_stats_response_stream(self, user_query: str, stats: Dict, emit_callback=None) -> Dict[str, Any]:
        """Generate streaming response for statistics queries"""
        if not self.llm:
            return {
                'user_query': user_query,
                'data_context': 'database statistics',
                'relevant_data': stats,
                'llm_response': 'LLM not configured. Statistics computed without AI analysis.',
                'data_count': stats.get('total_sitreps', 0)
            }
        system_prompt = "You are analyzing SITREP database statistics. Provide a clear, informative summary of the data patterns and key insights."
        user_prompt = f"""
        User Question: {user_query}
        Database Statistics:
        - Total SITREPs: {stats['total_sitreps']}
        - Recent (24h): {stats['recent_24h']}
        - By Severity: {json.dumps(stats['by_severity'], indent=2)}
        - By Status: {json.dumps(stats['by_status'], indent=2)}
        - By Incident Type: {json.dumps(stats['by_incident_type'], indent=2)}
        Please provide an analysis of these statistics.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        llm_response = self.llm.chat_completion_stream(messages, callback=emit_callback)
        return {
            'user_query': user_query,
            'data_context': 'database statistics',
            'relevant_data': stats,
            'llm_response': llm_response,
            'data_count': stats['total_sitreps']
        }