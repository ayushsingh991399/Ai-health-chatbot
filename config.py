import os
import streamlit as st

from langchain_cohere import ChatCohere
from langchain_community.tools import TavilySearchResults

COHERE_API_KEY = st.secrets["COHERE_API_KEY"]
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]

os.environ["CO_API_KEY"] = COHERE_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

llm = ChatCohere(
    model="command-nightly",
    temperature=0.3,
)

search_tool = TavilySearchResults(max_results=5)
