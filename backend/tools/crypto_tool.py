"""
Cryptocurrency Tool - CoinGecko API integration
"""
import httpx
from typing import Dict, Any
from core.tool_manager import BaseTool

class CryptoTool(BaseTool):
    """Cryptocurrency price tool using CoinGecko API"""
    
    def __init__(self):
        super().__init__()
        self.category = "finance"
        self.base_url = "https://api.coingecko.com/api/v3/simple/price"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        symbol = params.get("symbol", params.get("coin", "bitcoin")).lower()
        
        # Map common symbols
        symbol_map = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "doge": "dogecoin",
            "ada": "cardano",
            "dot": "polkadot"
        }
        
        symbol = symbol_map.get(symbol, symbol)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "ids": symbol,
                        "vs_currencies": "usd,eur",
                        "include_24hr_change": "true"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if symbol in data:
                        coin_data = data[symbol]
                        return {
                            "symbol": symbol.upper(),
                            "name": symbol.title(),
                            "price_usd": f"${coin_data['usd']:,.2f}",
                            "price_eur": f"€{coin_data['eur']:,.2f}",
                            "change_24h": f"{coin_data.get('usd_24h_change', 0):.2f}%",
                            "timestamp": "real-time"
                        }
        
        except Exception as e:
            pass
        
        # Demo data
        demo_prices = {
            "bitcoin": {"price": "$45,123.45", "change": "+2.34%"},
            "ethereum": {"price": "$2,456.78", "change": "-1.23%"},
            "dogecoin": {"price": "$0.08", "change": "+5.67%"}
        }
        
        demo_data = demo_prices.get(symbol, {"price": "$1,234.56", "change": "+0.00%"})
        
        return {
            "symbol": symbol.upper(),
            "name": symbol.title(),
            "price_usd": demo_data["price"],
            "change_24h": demo_data["change"],
            "status": "demo_data"
        }
    
    def get_description(self) -> str:
        return "Get current cryptocurrency prices and 24h changes"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "symbol": {
                "type": "string",
                "description": "Cryptocurrency symbol (e.g., bitcoin, ethereum, btc, eth)",
                "required": True
            }
        }