"""
Web fetching tool for retrieving content from URLs
"""
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from langchain.tools import tool

logger = logging.getLogger(__name__)


class WebFetchTool:
    """Tool for fetching web content"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetch content from a URL and extract text.

        Args:
            url: URL to fetch

        Returns:
            Dict with content, status, and metadata
        """
        try:
            logger.info(f"Fetching URL: {url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Chatbot Framework)'
            }

            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # Remove scripts and styles
            for script in soup(['script', 'style']):
                script.decompose()

            # Get visible text
            visible_text = soup.get_text(separator='\n', strip=True)

            # Also get hidden text (for injection detection)
            all_text = soup.get_text(separator='\n')

            result = {
                'url': url,
                'status_code': response.status_code,
                'visible_content': visible_text,
                'all_content': all_text,
                'content_length': len(visible_text),
                'success': True
            }

            logger.info(f"Successfully fetched {url} ({len(visible_text)} chars)")
            return result

        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'success': False
            }


# LangChain tool decorator
@tool
def fetch_url(url: str) -> str:
    """
    Fetch content from a web URL. Use this tool whenever a user asks you to fetch, get, retrieve, or access any URL.

    This tool can fetch content from ANY URL, including:
    - Internal URLs (like http://content-server:8181/page/welcome)
    - External URLs (like https://example.com or https://oastify.com)
    - Any http:// or https:// URL

    IMPORTANT: Always pass the COMPLETE URL including the protocol (http:// or https://).

    Args:
        url: The COMPLETE URL to fetch (must include http:// or https://)

    Returns:
        The text content of the web page
    """
    fetcher = WebFetchTool()
    result = fetcher.fetch(url)

    if result['success']:
        return result['visible_content']
    else:
        return f"Error fetching URL: {result.get('error', 'Unknown error')}"
