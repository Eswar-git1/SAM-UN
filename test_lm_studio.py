#!/usr/bin/env python3
"""
Test script for LM Studio integration with SITREP analysis
"""

import requests
import json
import sys

def test_lm_studio_connection():
    """Test if LM Studio is running and accessible"""
    LM_STUDIO_BASE_URL = "http://localhost:1234"
    
    try:
        # Test if LM Studio is running
        response = requests.get(f"{LM_STUDIO_BASE_URL}/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ LM Studio is running!")
            print(f"Available models: {len(models.get('data', []))}")
            for model in models.get('data', []):
                print(f"  - {model.get('id', 'Unknown')}")
            return True
        else:
            print(f"❌ LM Studio responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to LM Studio: {e}")
        print("\n📋 To fix this:")
        print("1. Open LM Studio application")
        print("2. Load a model (e.g., Llama, Mistral, etc.)")
        print("3. Go to the 'Developer' tab")
        print("4. Click 'Start Server' (default port 1234)")
        print("5. Ensure the server is running on http://localhost:1234")
        return False

def test_ai_insights_analysis():
    """Test the AI insights analysis with sample data"""
    # Sample SITREP data for testing
    sample_data = [
        {
            "id": 1,
            "severity": "High",
            "source": "Unit Alpha",
            "source_category": "Military",
            "status": "Open",
            "unit": "1st Battalion",
            "created_at": "2024-10-15 10:00:00"
        },
        {
            "id": 2,
            "severity": "Critical",
            "source": "Unit Bravo",
            "source_category": "Intelligence",
            "status": "Open",
            "unit": "2nd Battalion",
            "created_at": "2024-10-15 11:00:00"
        },
        {
            "id": 3,
            "severity": "Medium",
            "source": "Unit Charlie",
            "source_category": "Logistics",
            "status": "Closed",
            "unit": "3rd Battalion",
            "created_at": "2024-10-15 12:00:00"
        }
    ]
    
    LM_STUDIO_BASE_URL = "http://localhost:1234"
    
    # Prepare data summary
    data_summary = {
        "total_incidents": len(sample_data),
        "severity_distribution": {"High": 1, "Critical": 1, "Medium": 1},
        "source_categories": {"Military": 1, "Intelligence": 1, "Logistics": 1},
        "status_distribution": {"Open": 2, "Closed": 1},
        "unit_involvement": {"1st Battalion": 1, "2nd Battalion": 1, "3rd Battalion": 1},
        "recent_incident_samples": sample_data
    }
    
    # Create analysis prompt
    prompt = f"""
Analyze the following SITREP (Situation Report) data and provide comprehensive intelligence insights.

SITREP DATA:
{json.dumps(data_summary, indent=2)}

Please provide your analysis in the following JSON format:
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
            "severity": "High/Medium/Low"
        }}
    ],
    "trends": [
        {{
            "title": "Trend Title",
            "description": "Description of the trend and its trajectory", 
            "direction": "Upward/Downward/Stable"
        }}
    ],
    "summary": "A comprehensive summary of key findings and recommendations"
}}

Focus on:
1. PATTERNS: Recurring themes, common characteristics, operational patterns
2. ANOMALIES: Unusual events, outliers, unexpected developments
3. TRENDS: Changes over time, escalation/de-escalation, emerging threats
4. SUMMARY: Key insights, threat assessment, recommended actions

Provide military-grade analysis with actionable intelligence insights.
"""
    
    # Call LM Studio API
    payload = {
        "model": "local-model",
        "messages": [
            {
                "role": "system", 
                "content": "You are an expert military intelligence analyst specializing in SITREP (Situation Report) analysis. Provide detailed, actionable insights in JSON format."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.3
    }
    
    try:
        print("\n🔄 Testing AI insights analysis...")
        response = requests.post(
            f"{LM_STUDIO_BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            print("✅ LM Studio analysis successful!")
            print("\n📊 AI Response:")
            print("-" * 50)
            
            try:
                insights = json.loads(ai_response)
                print("📋 Patterns:")
                for pattern in insights.get("patterns", []):
                    print(f"  • {pattern.get('title', 'N/A')}: {pattern.get('description', 'N/A')}")
                
                print("\n⚠️ Anomalies:")
                for anomaly in insights.get("anomalies", []):
                    print(f"  • {anomaly.get('title', 'N/A')}: {anomaly.get('description', 'N/A')}")
                
                print("\n📈 Trends:")
                for trend in insights.get("trends", []):
                    print(f"  • {trend.get('title', 'N/A')}: {trend.get('description', 'N/A')}")
                
                print(f"\n📝 Summary: {insights.get('summary', 'N/A')}")
                
            except json.JSONDecodeError:
                print("⚠️ Response is not valid JSON, showing raw response:")
                print(ai_response[:500] + "..." if len(ai_response) > 500 else ai_response)
            
            return True
        else:
            print(f"❌ LM Studio API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to LM Studio: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing LM Studio Integration for SITREP AI Insights")
    print("=" * 60)
    
    # Test 1: Check LM Studio connection
    if not test_lm_studio_connection():
        print("\n❌ LM Studio connection test failed. Please start LM Studio first.")
        sys.exit(1)
    
    # Test 2: Test AI insights analysis
    if test_ai_insights_analysis():
        print("\n✅ All tests passed! LM Studio integration is working.")
    else:
        print("\n❌ AI insights analysis test failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()