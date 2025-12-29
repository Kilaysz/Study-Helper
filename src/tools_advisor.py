import os
import requests
from bs4 import BeautifulSoup
from langchain_community.utilities import SerpAPIWrapper 
from langchain_core.tools import tool

# --- HELPER FUNCTION (Was missing) ---
def scrape_url(url: str):
    """
    Scrapes text content from a URL for the deep_research tool.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Error: Status code {response.status_code}"
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        return text[:8000] # Limit to 8k chars to prevent context overflow
        
    except Exception as e:
        return f"Scraping failed: {str(e)}"

# --- TOOLS ---

@tool
def deep_research(query: str):
    """
    COMBINED TOOL: Searches Google (via SerpAPI) AND scrapes the top result.
    Use this for comprehensive research on a specific topic.
    """
    try:
        # A. Search
        search = SerpAPIWrapper()
        results = search.results(query)
        
        # B. Handle SerpAPI JSON Structure
        if "organic_results" not in results or not results["organic_results"]:
            return "No search results found on Google."
            
        # Get the best link (Top 1)
        top_result = results["organic_results"][0]
        link = top_result.get("link")
        title = top_result.get("title")
        snippet = top_result.get("snippet")
        
        print(f"🔗 Deep Research: Scaping {link}...")
        
        # C. Scrape it
        page_content = scrape_url(link)
        
        return f"""
        ### RESEARCH RESULT
        **Source:** {title}
        **URL:** {link}
        **Google Snippet:** {snippet}
        
        ### FULL PAGE CONTENT:
        {page_content}
        """
        
    except Exception as e:
        return f"Deep research failed: {e}"

@tool
def ncku_faculty_search(professor_name: str):
    """
    Specifically searches for a professor's latest contact info or lab page 
    on the NCKU CSIE website domain.
    """
    search = SerpAPIWrapper()
    # Restrict to university domain for accuracy
    query = f"site:csie.ncku.edu.tw {professor_name} lab research interests"
    return search.run(query)

def get_advisor_tool():
    return [
        ncku_faculty_search,
        deep_research
    ]