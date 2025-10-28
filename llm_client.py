"""
LLM Client module for SAM UN application
Supports both LM Studio (local) and OpenRouter (cloud) APIs
"""
import json
import requests
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Send chat completion request"""
        pass
    
    @abstractmethod
    def chat_completion_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000, callback=None):
        """Send streaming chat completion request"""
        pass


class LMStudioClient(LLMClient):
    """Client for communicating with LM Studio API (local)"""
    
    def __init__(self, base_url: str = "http://localhost:1234", model_name: str = None):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.session = requests.Session()
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from LM Studio"""
        try:
            response = self.session.get(f"{self.base_url}/v1/models")
            response.raise_for_status()
            data = response.json()
            return [model['id'] for model in data.get('data', [])]
        except Exception as e:
            print(f"Error getting models from LM Studio: {e}")
            return []
    
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Send chat completion request to LM Studio"""
        try:
            payload = {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            if self.model_name:
                payload["model"] = self.model_name
            
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
        
        except Exception as e:
            return f"Error communicating with LM Studio: {str(e)}"
    
    def chat_completion_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000, callback=None):
        """Send streaming chat completion request to LM Studio"""
        try:
            payload = {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            if self.model_name:
                payload["model"] = self.model_name
            
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=True
            )
            response.raise_for_status()
            
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                
                                if content:
                                    full_response += content
                                    if callback:
                                        callback('chatbot_stream_chunk', {'partial_response': full_response})
                        
                        except json.JSONDecodeError:
                            continue
            
            return full_response
        
        except Exception as e:
            error_msg = f"Error communicating with LM Studio: {str(e)}"
            if callback:
                callback('chatbot_error', {'error': error_msg})
            return error_msg


class OpenRouterClient(LLMClient):
    """Client for communicating with OpenRouter API (cloud)"""
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1", model_name: str = "openai/gpt-3.5-turbo"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sam-un-app.vercel.app",  # Optional: for analytics
            "X-Title": "SAM UN Application"  # Optional: for analytics
        })
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from OpenRouter"""
        try:
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            data = response.json()
            return [model['id'] for model in data.get('data', [])]
        except Exception as e:
            print(f"Error getting models from OpenRouter: {e}")
            # Return some common free models as fallback
            return [
                "openai/gpt-3.5-turbo",
                "anthropic/claude-3-haiku",
                "meta-llama/llama-3.1-8b-instruct:free",
                "microsoft/wizardlm-2-8x22b",
                "google/gemma-7b-it:free"
            ]
    
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Send chat completion request to OpenRouter"""
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
        
        except Exception as e:
            return f"Error communicating with OpenRouter: {str(e)}"
    
    def chat_completion_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000, callback=None):
        """Send streaming chat completion request to OpenRouter"""
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                stream=True
            )
            response.raise_for_status()
            
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                
                                if content:
                                    full_response += content
                                    if callback:
                                        callback('chatbot_stream_chunk', {'partial_response': full_response})
                        
                        except json.JSONDecodeError:
                            continue
            
            return full_response
        
        except Exception as e:
            error_msg = f"Error communicating with OpenRouter: {str(e)}"
            if callback:
                callback('chatbot_error', {'error': error_msg})
            return error_msg


def create_llm_client(provider: str = "openrouter", **kwargs) -> LLMClient:
    """Factory function to create appropriate LLM client"""
    if provider.lower() == "lmstudio":
        raise ValueError("LM Studio provider is no longer supported")
    elif provider.lower() == "openrouter":
        api_key = kwargs.get('api_key')
        if not api_key:
            raise ValueError("OpenRouter API key is required")
        
        return OpenRouterClient(
            api_key=api_key,
            base_url=kwargs.get('base_url', 'https://openrouter.ai/api/v1'),
            model_name=kwargs.get('model_name', 'openai/gpt-3.5-turbo')
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")