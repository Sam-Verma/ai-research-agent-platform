import httpx
from bs4 import BeautifulSoup
import structlog

logger = structlog.get_logger()

def scrape_website(url: str) -> str:
    """
    Scrapes the main text content of a given URL.
    Returns a string of the text content.
    """
    logger.info("Scraping website", url=url)
    
    try:
        # User-Agent to avoid simple blocks
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            text = soup.get_text(separator=' ')
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit the size to avoid token overflow
            max_chars = 15000 
            if len(text) > max_chars:
                text = text[:max_chars] + "... [Content Truncated]"
                
            return text
            
    except Exception as e:
        logger.error("Failed to scrape website", url=url, error=str(e))
        return f"Failed to scrape the website: {str(e)}"

scrape_tool_definition = {
    "type": "function",
    "function": {
        "name": "scrape_website",
        "description": "Scrapes the content of a specific webpage URL to extract detailed information.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL of the website to scrape."
                }
            },
            "required": ["url"]
        }
    }
}
