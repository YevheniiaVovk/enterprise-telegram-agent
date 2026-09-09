import asyncio  # 👈 обов'язковий імпорт
import logging
from typing import Optional
from ddgs import DDGS
from langchain.tools import tool
import requests

logger = logging.getLogger(__name__)


@tool
async def web_search(query: str) -> str:
    """Search the internet for current events, news, recent facts, or real-time information."""
    try:
        def _search():
            with DDGS() as ddgs:
                
                return list(ddgs.text(query, region="ua-uk", max_results=5))

        
        search_results = await asyncio.wait_for(
            asyncio.to_thread(_search),
            timeout=10.0
        )
        
        results = []
        for r in search_results:
            title = r.get("title", "No Title")
            snippet = r.get("body", "No Description")
            url = r.get("href", "")
            if url:
                results.append(f"Title: {title}\nSnippet: {snippet}\nURL: {url}")

        if not results:
            logger.warning(f"⚠️ [WEB SEARCH] No results found for query: {query}")
            return "No search results found. Try rephrasing the search query."

        logger.info(f"✅ [WEB SEARCH] Found {len(results)} results for query: {query}")
        return "\n\n---\n\n".join(results)

    except asyncio.TimeoutError:
        logger.error(f"❌ [WEB SEARCH TIMEOUT]: Query '{query}' took too long.")
        return "Search error: DuckDuckGo response timed out."
    except Exception as e:
        logger.error(f"❌ [WEB SEARCH ERROR]: {e}")
        return f"Error performing web search: {str(e)}"


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search for relevant information in the internal knowledge base.

    Args:
        query: Search query string

    Returns:
        Search results from the knowledge base
    """
    return f"Search results for: '{query}' (mock data - RAG coming soon)"


@tool
def execute_http_action(
    url: str, method: str = "GET", payload: Optional[dict] = None
) -> str:
    """
    Make an HTTP request to an external API.
    Used to retrieve data from Weather API, Crypto API, etc.

    Args:
        url: The URL for the request
        method: HTTP method (GET, POST, PUT, DELETE)
        payload: JSON data for POST/PUT requests

    Returns:
        The response from the API as a string
    """
    try:
        method_upper = method.upper()
        if method_upper == "GET":
            response = requests.get(url, timeout=10)
        elif method_upper == "POST":
            response = requests.post(url, json=payload, timeout=10)
        elif method_upper == "PUT":
            response = requests.put(url, json=payload, timeout=10)
        elif method_upper == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return f"Unknown HTTP method: {method}"

        if response.status_code == 200:
            return response.text
        return f"API Error: Status {response.status_code} - {response.text}"

    except requests.exceptions.Timeout:
        return "Request timeout - API took too long to respond"
    except requests.exceptions.ConnectionError:
        return "Connection error - Could not reach the API"
    except Exception as e:
        return f"Request error: {str(e)}"


@tool
def get_user_profile(user_id: int) -> dict:
    """
    Get a user's profile based on their Telegram ID.
    Reads from the database via SQLAlchemy.

    Args:
        user_id: The user's Telegram ID (integer)

    Returns:
        Profile data dictionary containing user information
    """
    return {
        "user_id": user_id,
        "name": f"User_{user_id}",
        "created_at": "2026-08-17",
        "conversation_count": 0,
        "status": "active",
        "language": "uk",
    }