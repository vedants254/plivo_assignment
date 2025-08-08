"""
Model Configuration for Multi-Modal AI Application
Configured for Vercel deployment using Hugging Face Inference Endpoints only
"""

import os
from typing import Dict, Any

# API-only Model configurations for Vercel deployment
MODEL_CONFIGS = {
    "vision_models": {
        "deepseek-vl-api": {
            "model_id": "deepseek-ai/deepseek-vl-1.3b-chat",
            "api_url": "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-vl-1.3b-chat",
            "description": "DeepSeek-VL 1.3B - Vision-language model via Hugging Face API",
            "deployment": "api_only",
            "recommended": True,
            "features": ["image_analysis", "visual_reasoning", "multimodal_chat"]
        }
    },
    
    "text_models": {
        "mistral-7b-instruct-api": {
            "model_id": "mistralai/Mistral-7B-Instruct-v0.3",
            "api_url": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
            "description": "Mistral 7B Instruct v0.3 - Text generation and summarization via Hugging Face API",
            "deployment": "api_only",
            "recommended": True,
            "features": ["text_generation", "summarization", "instruction_following"]
        }
    }
}

# API endpoints for Vercel deployment
API_ENDPOINTS = {
    "vision": {
        "deepseek-vl": "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-vl-1.3b-chat"
    },
    "text": {
        "mistral-7b-instruct": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
    }
}

# Prompt templates for API models
PROMPT_TEMPLATES = {
    "deepseek_vl": {
        "image_analysis": "Describe this image in detail, including objects, people, colors, setting, activities, and overall atmosphere.",
        "visual_reasoning": "Analyze this image and answer the following question: {question}",
        "multimodal_chat": "Look at this image and {instruction}"
    },
    
    "mistral_7b": {
        "summarization": """<s>[INST] Please provide a concise summary of the following text. Focus on the main points, key information, and important details:

{text}

Provide a clear, informative summary in 2-3 paragraphs. [/INST]""",
        
        "instruction_following": """<s>[INST] {instruction} [/INST]""",
        
        "text_generation": """<s>[INST] {prompt} [/INST]"""
    }
}

def get_deepseek_vl_payload(image_base64: str, prompt: str):
    """Format payload for DeepSeek-VL API"""
    return {
        "inputs": {
            "text": prompt,
            "image": image_base64
        },
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "do_sample": True
        }
    }

def get_mistral_prompt(text: str, task_type: str = "summarization"):
    """Format prompt for Mistral 7B API"""
    template = PROMPT_TEMPLATES["mistral_7b"][task_type]
    
    if task_type == "summarization":
        return template.format(text=text)
    elif task_type == "instruction_following":
        return template.format(instruction=text)
    elif task_type == "text_generation":
        return template.format(prompt=text)
    else:
        return f"<s>[INST] {text} [/INST]"

def get_mistral_payload(prompt: str, max_tokens: int = 300):
    """Format payload for Mistral 7B API"""
    return {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }

def check_vercel_compatibility():
    """Check if configuration is compatible with Vercel deployment"""
    return {
        "vercel_compatible": True,
        "deployment_type": "api_only",
        "execution_time_limit": "10_seconds",
        "gpu_required": False,
        "local_model_loading": False,
        "quantization": False,
        "recommendations": [
            "All inference done via Hugging Face API",
            "No local model loading required",
            "Suitable for Vercel serverless functions",
            "API calls may take 3-10 seconds per request"
        ]
    }

def get_default_models():
    """Get default models for Vercel deployment"""
    return {
        "vision": "deepseek-vl-api",
        "text": "mistral-7b-instruct-api"
    }

def get_api_config():
    """Get API configuration for Vercel deployment"""
    return {
        "timeout": 30,
        "retry_attempts": 2,
        "fallback_enabled": False,
        "models": {
            "vision": {
                "endpoint": API_ENDPOINTS["vision"]["deepseek-vl"],
                "model_name": "DeepSeek-VL-1.3B-Chat"
            },
            "text": {
                "endpoint": API_ENDPOINTS["text"]["mistral-7b-instruct"],
                "model_name": "Mistral-7B-Instruct-v0.3"
            }
        }
    }