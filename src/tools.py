import os
import base64
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_experimental.utilities import PythonREPL
from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain_community.tools.wolfram_alpha import WolframAlphaQueryRun
from langchain_core.tools import tool
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage

# ... existing search tools ...
def get_web_search_tool():
    return TavilySearchResults(max_results=3)

def get_arxiv_tool():
    arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=2000)
    return ArxivQueryRun(api_wrapper=arxiv_wrapper)

def get_wiki_tool():
    wiki_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
    return WikipediaQueryRun(api_wrapper=wiki_wrapper)

@tool
def python_calculator(code: str):
    """
    Use this to execute Python code for math calculations.
    Input should be valid python code string.
    """
    repl = PythonREPL()
    try:
        return repl.run(code)
    except Exception as e:
        return f"Error executing code: {e}"

def get_wolfram_tool():
    wrapper = WolframAlphaAPIWrapper()
    return WolframAlphaQueryRun(api_wrapper=wrapper)

# --- NEW VISION TOOL ---
@tool
def describe_image(image_path: str):
    """
    Use this tool to 'see' an image. 
    Pass the file path of an image (JPEG/PNG), and it returns a detailed text description.
    Useful for charts, diagrams, or photos.
    """
    try:
        # 1. Initialize the Vision Model (Llava)
        # Ensure you run 'ollama pull llava' first!
        vision_llm = ChatOllama(model="llava")
        
        # 2. Convert Image to Base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
        # 3. Ask the model to describe it
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Describe this image in detail. If it's a chart or graph, explain the data."},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"},
            ]
        )
        
        response = vision_llm.invoke([message])
        return f"Image Description: {response.content}"
        
    except Exception as e:
        return f"Error reading image: {str(e)}"
    
    
def get_all_tools():
    return [
        get_web_search_tool(),
        get_arxiv_tool(),
        get_wiki_tool(),
        python_calculator,
        get_wolfram_tool(),
        describe_image 
    ]