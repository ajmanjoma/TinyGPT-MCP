"""
Search Tool - Web search using DuckDuckGo API
"""
import httpx
from typing import Dict, Any
from core.tool_manager import BaseTool

class SearchTool(BaseTool):
    """Web search tool using DuckDuckGo API"""
    
    def __init__(self):
        super().__init__()
        self.category = "information"
        self.base_url = "https://api.duckduckgo.com/"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", params.get("q", "latest news"))
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": "1",
                        "skip_disambig": "1"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Try instant answer first
                    if data.get("AbstractText"):
                        return {
                            "query": query,
                            "result": data["AbstractText"],
                            "source": data.get("AbstractSource", "DuckDuckGo"),
                            "url": data.get("AbstractURL", ""),
                            "type": "instant_answer"
                        }
                    
                    # Try related topics
                    if data.get("RelatedTopics"):
                        first_topic = data["RelatedTopics"][0]
                        if isinstance(first_topic, dict) and "Text" in first_topic:
                            return {
                                "query": query,
                                "result": first_topic["Text"],
                                "source": "DuckDuckGo",
                                "url": first_topic.get("FirstURL", ""),
                                "type": "related_topic"
                            }
        
        except Exception as e:
            pass
        
        # Demo data
        return {
            "query": query,
            "result": f"Search results for '{query}': This is a demonstration search result. In production, this would contain actual search results from DuckDuckGo API with relevant information, links, and sources.",
            "source": "DuckDuckGo (demo)",
            "type": "demo_result",
            "status": "demo_data"
        }
    
    def get_description(self) -> str:
        return "Search the web for information using DuckDuckGo"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "Search query or question",
                "required": True
            }
        }