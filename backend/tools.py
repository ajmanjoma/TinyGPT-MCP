"""
Tool implementations for TinyGPT-MCP
Implements various tools that can be called by the model
"""
import httpx
import json
from typing import Dict, Any, Optional
import os
from datetime import datetime

class ToolRegistry:
    """Registry of available tools for the MCP system"""
    
    def __init__(self):
        self.tools = {
            "weather": WeatherTool(),
            "crypto_price": CryptoPriceTool(),
            "wiki": WikipediaTool(),
            "search": SearchTool(),
            "joke": JokeTool(),
            "news": NewsTool()
        }
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool with given arguments"""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool = self.tools[tool_name]
        return await tool.execute(arguments)
    
    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get descriptions of all available tools"""
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append({
                "name": name,
                "description": tool.get_description(),
                "parameters": tool.get_parameters()
            })
        return descriptions

class BaseTool:
    """Base class for all tools"""
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        """Execute the tool with given arguments"""
        raise NotImplementedError
    
    def get_description(self) -> str:
        """Get tool description"""
        raise NotImplementedError
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get tool parameters schema"""
        raise NotImplementedError

class WeatherTool(BaseTool):
    """Weather information tool using OpenWeatherMap API"""
    
    def __init__(self):
        # For demo purposes, we'll use a free weather API or mock data
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "demo_key")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        city = arguments.get("query", arguments.get("city", "London"))
        
        # For demo purposes, return mock data
        # In production, uncomment the API call below
        
        """
        async with httpx.AsyncClient() as client:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = await client.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "city": data["name"],
                    "temperature": data["main"]["temp"],
                    "description": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"]
                }
            else:
                return {"error": "Failed to fetch weather data"}
        """
        
        # Mock weather data for demo
        return {
            "city": city,
            "temperature": "22°C",
            "description": "Partly cloudy",
            "humidity": "65%",
            "status": "demo_data"
        }
    
    def get_description(self) -> str:
        return "Get current weather information for a specific city"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "city": {
                "type": "string",
                "description": "City name to get weather for"
            }
        }

class CryptoPriceTool(BaseTool):
    """Cryptocurrency price tool using CoinGecko API"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3/simple/price"
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        symbol = arguments.get("query", arguments.get("symbol", "bitcoin"))
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "ids": symbol,
                    "vs_currencies": "usd"
                }
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if symbol in data:
                        return {
                            "symbol": symbol,
                            "price": f"${data[symbol]['usd']:,}",
                            "currency": "USD",
                            "timestamp": datetime.now().isoformat()
                        }
                
                # Fallback mock data
                return {
                    "symbol": symbol,
                    "price": "$45,123.45" if symbol == "bitcoin" else "$2,456.78",
                    "currency": "USD",
                    "status": "demo_data"
                }
        
        except Exception as e:
            return {"error": f"Failed to fetch crypto price: {str(e)}"}
    
    def get_description(self) -> str:
        return "Get current cryptocurrency price in USD"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "symbol": {
                "type": "string",
                "description": "Cryptocurrency symbol (e.g., bitcoin, ethereum)"
            }
        }

class WikipediaTool(BaseTool):
    """Wikipedia summary tool"""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/api/rest_v1/page/summary"
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        topic = arguments.get("query", arguments.get("topic", "Python programming"))
        
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/{topic.replace(' ', '_')}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("extract", f"No summary found for {topic}")
                
                # Fallback mock data
                return f"Wikipedia summary for '{topic}': This is a demonstration summary. In production, this would contain the actual Wikipedia extract for the requested topic."
        
        except Exception as e:
            return f"Error fetching Wikipedia summary: {str(e)}"
    
    def get_description(self) -> str:
        return "Get Wikipedia summary for a topic"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "topic": {
                "type": "string",
                "description": "Topic to search on Wikipedia"
            }
        }

class SearchTool(BaseTool):
    """Web search tool using DuckDuckGo API"""
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        query = arguments.get("query", "general search")
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "q": query,
                    "format": "json",
                    "no_html": "1"
                }
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Try to get instant answer first
                    if data.get("AbstractText"):
                        return data["AbstractText"]
                    
                    # Otherwise, get first result
                    if data.get("Results") and len(data["Results"]) > 0:
                        return data["Results"][0].get("Text", "No detailed results found")
                
                # Fallback mock data
                return f"Search results for '{query}': This is a demonstration search result. In production, this would contain actual search results from DuckDuckGo API."
        
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def get_description(self) -> str:
        return "Search the web for information"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "Search query"
            }
        }

class JokeTool(BaseTool):
    """Joke tool using JokeAPI"""
    
    def __init__(self):
        self.base_url = "https://v2.jokeapi.dev/joke/Any"
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "blacklistFlags": "nsfw,religious,political,racist,sexist,explicit"
                }
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data["type"] == "single":
                        return data["joke"]
                    else:
                        return f"{data['setup']} {data['delivery']}"
                
                # Fallback joke
                return "Why do programmers prefer dark mode? Because light attracts bugs! 🐛"
        
        except Exception as e:
            return "Why don't scientists trust atoms? Because they make up everything! ⚛️"
    
    def get_description(self) -> str:
        return "Get a random joke"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {}

class NewsTool(BaseTool):
    """News tool - simplified version"""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY", "demo_key")
        self.base_url = "https://newsapi.org/v2/everything"
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        topic = arguments.get("query", arguments.get("topic", "technology"))
        
        # For demo purposes, return mock news
        # In production, implement actual NewsAPI integration
        
        """
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "q": topic,
                    "apiKey": self.api_key,
                    "language": "en",
                    "sortBy": "publishedAt"
                }
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])
                    
                    if articles:
                        article = articles[0]
                        return f"{article['title']} - {article['description']}"
                
                return f"No recent news found for {topic}"
        
        except Exception as e:
            return f"News error: {str(e)}"
        """
        
        # Mock news data
        return f"Latest news on '{topic}': This is a demonstration news article. In production, this would show real headlines and summaries from NewsAPI.org for the requested topic."
    
    def get_description(self) -> str:
        return "Get latest news articles on a topic"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "topic": {
                "type": "string",
                "description": "News topic to search for"
            }
        }