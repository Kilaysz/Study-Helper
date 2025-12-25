import os
import base64
import requests
import mimetypes
from bs4 import BeautifulSoup

from langchain_community.utilities import SerpAPIWrapper 
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper, WolframAlphaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, WolframAlphaQueryRun
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch

try:
    from langchain_ollama import ChatOllama
except ImportError:
    from langchain_community.chat_models import ChatOllama


# --- 1. Helper Function for Scraping (Reusable) ---
def scrape_url(url: str):
    """
    Helper function to scrape text from a URL using BeautifulSoup.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Error: Failed to load page (Status: {response.status_code})"
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Cleanup: Remove scripts, styles, nav, footer
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
            
        text = soup.get_text(separator="\n")
        
        # Clean whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)
        
        return clean_text[:30000] 
    except Exception as e:
        return f"Scraping failed: {str(e)}"

# --- 2. The Individual Tools (UPDATED) ---

@tool
def google_search(query: str):
    """
    Performs a standard Google Search using SerpAPI.
    Returns snippets only. Good for quick facts.
    """
    # Requires SERPAPI_API_KEY in .env
    search = SerpAPIWrapper()
    return search.run(query)

@tool
def scrape_website(url: str):
    """
    Scrapes the text content from a specific URL.
    Use this if you already have a link you want to read.
    """
    return scrape_url(url)

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
        
        # B. Handle SerpAPI JSON Structure (Different from Serper)
        # SerpAPI uses 'organic_results' instead of 'organic'
        if "organic_results" not in results or not results["organic_results"]:
            return "No search results found on Google."
            
        # Get the best link (Top 1)
        top_result = results["organic_results"][0]
        link = top_result.get("link")
        title = top_result.get("title")
        snippet = top_result.get("snippet")
        
        print(f"🔗 Found Link: {link} ({title})")
        
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

# --- Other Tools (Unchanged) ---

def get_web_search_tool():
    return TavilySearch(max_results=3)

def get_arxiv_tool():
    arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=2000)
    return ArxivQueryRun(api_wrapper=arxiv_wrapper)

def get_wiki_tool():
    wiki_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
    return WikipediaQueryRun(api_wrapper=wiki_wrapper)

def get_wolfram_tool():
    wrapper = WolframAlphaAPIWrapper()
    return WolframAlphaQueryRun(api_wrapper=wrapper)

@tool
def python_calculator(code: str):
    """
    Use this to execute Python code for math calculations.
    Input should be a valid python code string.
    """
    repl = PythonREPL()
    try:
        result = repl.run(code)
        return f"Result: {result}"
    except Exception as e:
        return f"Error executing code: {e}"

@tool
def describe_image(image_path: str):
    """
    Use this tool to 'see' an image. 
    Pass the full file path of an image (e.g., 'data/chart.png').
    """
    if not os.path.exists(image_path):
        return f"Error: Image file not found at {image_path}"

    try:
        vision_llm = ChatOllama(model="llava", temperature=0)
        
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg"

        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Describe this image in detail. If it's a chart, explain the data."},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}},
            ]
        )
        
        response = vision_llm.invoke([message])
        return f"Image Description: {response.content}"
        
    except Exception as e:
        return f"Error processing image: {str(e)}"

def get_all_tools():
    return [
        get_web_search_tool(),
        get_arxiv_tool(),
        get_wiki_tool(),
        get_wolfram_tool(),
        python_calculator,
        describe_image,
        google_search,    # Now uses SerpAPI
        scrape_website,
        deep_research,    # Now uses SerpAPI
    ]