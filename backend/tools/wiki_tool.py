"""
Wikipedia Tool - Wikipedia API integration
"""
import httpx
from typing import Dict, Any
from core.tool_manager import BaseTool

class WikiTool(BaseTool):
    """Wikipedia summary tool"""
    
    def __init__(self):
        super().__init__()
        self.category = "information"
        self.base_url = "https://en.wikipedia.org/api/rest_v1/page/summary"
    
    async def execute(self, params: Dict[str, Any]) -> str:
        topic = params.get("topic", params.get("query", "Artificial Intelligence"))
        
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/{topic.replace(' ', '_')}"
                response = await client.get(url, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    extract = data.get("extract", "")
                    
                    if extract:
                        # Limit to reasonable length
                        if len(extract) > 500:
                            extract = extract[:500] + "..."
                        
                        return {
                            "title": data.get("title", topic),
                            "summary": extract,
                            "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                            "source": "Wikipedia"
                        }
        
        except Exception as e:
            pass
        
        # Demo data
        return {
            "title": topic,
            "summary": f"This is a demonstration summary for '{topic}'. In production, this would contain the actual Wikipedia extract with comprehensive information about the topic, including key facts, history, and relevant details.",
            "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "source": "Wikipedia (demo)",
            "status": "demo_data"
        }
    
    def get_description(self) -> str:
        return "Get Wikipedia summary and information about any topic"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "topic": {
                "type": "string",
                "description": "Topic to search on Wikipedia",
                "required": True
            }
        }