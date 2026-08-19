from langchain.tools import tool
import httpx
from typing import Optional


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search for relevant information in the knowledge base.
    
    Args:
        query: Search query
        
    Returns:
        Search results from the knowledge base
    # Just a mock for now—we'll add RAG later
    """
    results = f"Search results for: '{query}'"
    return results


@tool
async def execute_http_action(url: str, method: str = "GET", payload: Optional[dict] = None) -> str:
    """
    Make an HTTP request to an external API.
    Used to retrieve data from the Weather API, Crypto API, etc.

    Args:
        url: The URL for the request
        method: HTTP method (GET, POST)
        payload: JSON data for POST

    Returns:
        The response from the API
     """
    try:
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url)
            elif method.upper() == "POST":
                response = await client.post(url, json=payload)
            else:
                return f"Unknown method: {method}"
            
            if response.status_code == 200:
                return response.text
            else:
                return f"API Error: {response.status_code}"
    except Exception as e:
        return f"Request error: {str(e)}"


@tool
def get_user_profile(user_id: int) -> dict:
    """
    Get a user's profile based on their Telegram ID.
    Reads from the database via the ToolRuntime context.

    Args:
        user_id: The user's Telegram ID

    Returns:
        Profile data (name, history, settings)
    """
    
    user_profile = {
        "user_id": user_id,
        "name": f"User_{user_id}",
        "created_at": "2026-08-17",
        "conversation_count": 0,
    }
    return user_profile