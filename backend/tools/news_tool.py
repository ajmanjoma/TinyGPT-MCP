"""
News Tool - NewsAPI integration
"""
import httpx
from typing import Dict, Any, List
from core.tool_manager import BaseTool

class NewsTool(BaseTool):
    """News tool using NewsAPI"""
    
    def __init__(self):
        super().__init__()
        self.category = "information"
        self.api_key = "demo_key"  # Replace with actual NewsAPI key
        self.base_url = "https://newsapi.org/v2/everything"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        topic = params.get("topic", params.get("query", "technology"))
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "q": topic,
                        "apiKey": self.api_key,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 3
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])
                    
                    if articles:
                        formatted_articles = []
                        for article in articles[:3]:
                            formatted_articles.append({
                                "title": article["title"],
                                "description": article["description"],
                                "source": article["source"]["name"],
                                "url": article["url"],
                                "published": article["publishedAt"]
                            })
                        
                        return {
                            "topic": topic,
                            "articles": formatted_articles,
                            "total_results": data.get("totalResults", 0)
                        }
        
        except Exception as e:
            pass
        
        # Demo data
        return {
            "topic": topic,
            "articles": [
                {
                    "title": f"Latest developments in {topic}",
                    "description": f"This is a demonstration news article about {topic}. In production, this would show real headlines and summaries from NewsAPI.org.",
                    "source": "Demo News",
                    "url": "https://example.com/news",
                    "published": "2024-01-15T10:00:00Z"
                }
            ],
            "total_results": 1,
            "status": "demo_data"
        }
    
    def get_description(self) -> str:
        return "Get latest news articles on any topic"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "topic": {
                "type": "string",
                "description": "News topic or keyword to search for",
                "required": True
            }
        }