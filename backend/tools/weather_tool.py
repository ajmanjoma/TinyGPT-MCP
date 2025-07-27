"""
Weather Tool - OpenWeatherMap API integration
"""
import httpx
from typing import Dict, Any
from core.tool_manager import BaseTool

class WeatherTool(BaseTool):
    """Weather information tool using OpenWeatherMap API"""
    
    def __init__(self):
        super().__init__()
        self.category = "information"
        self.api_key = "demo_key"  # Replace with actual API key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        location = params.get("location", params.get("city", "London"))
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "q": location,
                        "appid": self.api_key,
                        "units": "metric"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "location": data["name"],
                        "temperature": f"{data['main']['temp']}°C",
                        "description": data["weather"][0]["description"].title(),
                        "humidity": f"{data['main']['humidity']}%",
                        "pressure": f"{data['main']['pressure']} hPa",
                        "wind_speed": f"{data.get('wind', {}).get('speed', 0)} m/s"
                    }
        
        except Exception as e:
            # Fallback to demo data
            pass
        
        # Demo data for testing
        return {
            "location": location,
            "temperature": "22°C",
            "description": "Partly Cloudy",
            "humidity": "65%",
            "pressure": "1013 hPa",
            "wind_speed": "3.2 m/s",
            "status": "demo_data"
        }
    
    def get_description(self) -> str:
        return "Get current weather information for any city worldwide"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "location": {
                "type": "string",
                "description": "City name or location to get weather for",
                "required": True
            }
        }
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "location" in params or "city" in params