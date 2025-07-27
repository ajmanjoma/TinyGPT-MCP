"""
Joke Tool - JokeAPI integration
"""
import httpx
import random
from typing import Dict, Any
from core.tool_manager import BaseTool

class JokeTool(BaseTool):
    """Joke tool using JokeAPI"""
    
    def __init__(self):
        super().__init__()
        self.category = "entertainment"
        self.base_url = "https://v2.jokeapi.dev/joke/Any"
        
        # Fallback jokes
        self.fallback_jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
            "Why don't scientists trust atoms? Because they make up everything! ⚛️",
            "How do you organize a space party? You planet! 🚀",
            "Why did the scarecrow win an award? He was outstanding in his field! 🌾",
            "What do you call a fake noodle? An impasta! 🍝"
        ]
    
    async def execute(self, params: Dict[str, Any]) -> str:
        category = params.get("category", "Any")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://v2.jokeapi.dev/joke/{category}",
                    params={
                        "blacklistFlags": "nsfw,religious,political,racist,sexist,explicit"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data["type"] == "single":
                        return data["joke"]
                    else:
                        return f"{data['setup']} {data['delivery']}"
        
        except Exception as e:
            pass
        
        # Return random fallback joke
        return random.choice(self.fallback_jokes)
    
    def get_description(self) -> str:
        return "Get a random clean joke for entertainment"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "category": {
                "type": "string",
                "description": "Joke category (Programming, Miscellaneous, Dark, Pun, Spooky, Christmas)",
                "required": False,
                "default": "Any"
            }
        }