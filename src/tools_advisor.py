import os
import base64
import requests
import mimetypes
from bs4 import BeautifulSoup

from langchain_community.utilities import SerpAPIWrapper 
from langchain_core.tools import tool

try:
    from langchain_ollama import ChatOllama
except ImportError:
    from langchain_community.chat_models import ChatOllama


@tool
def ncku_faculty_search(professor_name: str):
    """
    Specifically searches for a professor's latest contact info or lab page 
    on the NCKU CSIE website domain.
    """
    search = SerpAPIWrapper()
    # We force the search to restrict results to the university domain
    query = f"site:csie.ncku.edu.tw {professor_name} lab research interests"
    return search.run(query)


def get_advisor_tool():
    return [
        ncku_faculty_search
    ]