"""
Utility functions for AI content generation.
"""
import json
import os
import time
from typing import List, Dict, Any, Optional

import anthropic
import openai
from django.core.management.base import CommandError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_response(prompt: str, system_message: str) -> str:
    """
    Get a response from OpenAI API.
    
    Args:
        prompt: The prompt to send to OpenAI
        system_message: The system message to set the context
        
    Returns:
        The text response from OpenAI
    """
    # Set up the OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Less expensive model
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048,  # Cap the token usage
        )
        return response.choices[0].message.content
    except Exception as e:
        raise CommandError(f"Error calling OpenAI API: {str(e)}")


def get_claude_response(prompt: str, system_message: str) -> str:
    """
    Get a response from Anthropic Claude API.
    
    Args:
        prompt: The prompt to send to Claude
        system_message: The system message to set the context
        
    Returns:
        The text response from Claude
    """
    # Set up the Claude API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Less expensive model
            max_tokens=1000,  # Cap the token usage
            system=system_message,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        raise CommandError(f"Error calling Claude API: {str(e)}")


def extract_json_from_response(response: str) -> str:
    """
    Extract JSON content from an AI response.
    
    Args:
        response: The raw text response from the AI
        
    Returns:
        The extracted JSON content
    """
    json_content = response
    
    # If the response includes code blocks, extract the JSON
    if "```json" in response:
        json_content = response.split("```json")[1].split("```")[0].strip()
    elif "```" in response:
        json_content = response.split("```")[1].split("```")[0].strip()
        
    return json_content


def is_similar_text(text1: str, text2: str, min_length: int = 20) -> bool:
    """
    Check if two texts are similar by comparing simplified versions.
    
    Args:
        text1: First text to compare
        text2: Second text to compare
        min_length: Minimum length for partial matching
        
    Returns:
        True if texts are similar, False otherwise
    """
    # Simplify both texts: lowercase and only alphanumeric chars
    simplified1 = ''.join(c.lower() for c in text1 if c.isalnum() or c.isspace()).strip()
    simplified2 = ''.join(c.lower() for c in text2 if c.isalnum() or c.isspace()).strip()
    
    # Exact match on simplified text
    if simplified1 == simplified2:
        return True
        
    # For longer texts, check if one is contained in the other
    if len(simplified1) > min_length and (
        simplified1 in simplified2 or simplified2 in simplified1
    ):
        return True
        
    return False