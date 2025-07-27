"""
TinyGPT Inference Engine
A lightweight text generation model with tool-calling capabilities
"""
import random
import re
from typing import List, Dict, Any

class TinyGPT:
    """
    A simplified GPT-style model that can generate text responses
    and embed tool calls using the MCP format: <tool>function_name(args)</tool>
    """
    
    def __init__(self):
        self.model_name = "TinyGPT-v1.0"
        self.temperature = 0.7
        
        # Predefined response patterns for demonstration
        # In a real implementation, this would be replaced with actual model weights
        self.response_patterns = {
            "weather": [
                "Let me check the weather for you. <tool>weather({city})</tool>",
                "I'll get the current weather conditions. <tool>weather({city})</tool>",
                "Checking weather data... <tool>weather({city})</tool>"
            ],
            "crypto": [
                "Let me fetch the latest cryptocurrency price. <tool>crypto_price({symbol})</tool>",
                "I'll check the current market price. <tool>crypto_price({symbol})</tool>",
                "Getting crypto market data... <tool>crypto_price({symbol})</tool>"
            ],
            "wikipedia": [
                "I'll search Wikipedia for that information. <tool>wiki({topic})</tool>",
                "Let me look that up on Wikipedia. <tool>wiki({topic})</tool>",
                "Searching Wikipedia... <tool>wiki({topic})</tool>"
            ],
            "search": [
                "Let me search for that information. <tool>search({query})</tool>",
                "I'll find the latest information on that. <tool>search({query})</tool>",
                "Searching the web... <tool>search({query})</tool>"
            ],
            "joke": [
                "Here's a joke for you! <tool>joke()</tool>",
                "Let me tell you something funny! <tool>joke()</tool>",
                "Time for some humor! <tool>joke()</tool>"
            ],
            "news": [
                "Let me get the latest news on that topic. <tool>news({topic})</tool>",
                "I'll fetch recent news articles. <tool>news({topic})</tool>",
                "Checking current news... <tool>news({topic})</tool>"
            ]
        }
    
    def _detect_intent_and_entities(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Simple intent detection and entity extraction
        In a real model, this would be learned from training data
        """
        prompt_lower = prompt.lower()
        intents = []
        
        # Weather detection
        weather_keywords = ["weather", "temperature", "rain", "sunny", "cloudy", "forecast"]
        cities = self._extract_cities(prompt)
        if any(keyword in prompt_lower for keyword in weather_keywords) and cities:
            for city in cities:
                intents.append({"type": "weather", "city": city})
        
        # Crypto detection
        crypto_keywords = ["price", "crypto", "bitcoin", "ethereum", "btc", "eth", "coin"]
        crypto_symbols = self._extract_crypto_symbols(prompt)
        if any(keyword in prompt_lower for keyword in crypto_keywords):
            if crypto_symbols:
                for symbol in crypto_symbols:
                    intents.append({"type": "crypto", "symbol": symbol})
            else:
                # Default to BTC if crypto mentioned but no specific symbol
                intents.append({"type": "crypto", "symbol": "bitcoin"})
        
        # Wikipedia detection
        wiki_keywords = ["wikipedia", "wiki", "summary", "information about", "tell me about"]
        if any(keyword in prompt_lower for keyword in wiki_keywords):
            topic = self._extract_wiki_topic(prompt)
            if topic:
                intents.append({"type": "wikipedia", "topic": topic})
        
        # Search detection
        search_keywords = ["search", "find", "who won", "latest", "recent"]
        if any(keyword in prompt_lower for keyword in search_keywords):
            query = self._extract_search_query(prompt)
            if query:
                intents.append({"type": "search", "query": query})
        
        # Joke detection
        joke_keywords = ["joke", "funny", "humor", "laugh", "amusing"]
        if any(keyword in prompt_lower for keyword in joke_keywords):
            intents.append({"type": "joke"})
        
        # News detection
        news_keywords = ["news", "headlines", "latest news", "current events"]
        if any(keyword in prompt_lower for keyword in news_keywords):
            topic = self._extract_news_topic(prompt)
            if topic:
                intents.append({"type": "news", "topic": topic})
        
        return intents
    
    def _extract_cities(self, prompt: str) -> List[str]:
        """Extract city names from the prompt"""
        # Simple pattern matching - in production, use NER models
        cities = []
        common_cities = ["paris", "london", "new york", "tokyo", "berlin", "madrid", "rome", "moscow", "beijing", "sydney"]
        
        prompt_lower = prompt.lower()
        for city in common_cities:
            if city in prompt_lower:
                cities.append(city.title())
        
        # Also check for capitalized words that might be cities
        words = prompt.split()
        for word in words:
            if word.istitle() and len(word) > 2 and word.lower() not in ["the", "and", "for", "what", "how"]:
                cities.append(word)
        
        return list(set(cities))  # Remove duplicates
    
    def _extract_crypto_symbols(self, prompt: str) -> List[str]:
        """Extract cryptocurrency symbols from the prompt"""
        crypto_map = {
            "bitcoin": "bitcoin",
            "btc": "bitcoin",
            "ethereum": "ethereum",
            "eth": "ethereum",
            "dogecoin": "dogecoin",
            "doge": "dogecoin",
            "cardano": "cardano",
            "ada": "cardano",
            "polkadot": "polkadot",
            "dot": "polkadot"
        }
        
        symbols = []
        prompt_lower = prompt.lower()
        
        for key, value in crypto_map.items():
            if key in prompt_lower:
                symbols.append(value)
        
        return list(set(symbols))
    
    def _extract_wiki_topic(self, prompt: str) -> str:
        """Extract Wikipedia topic from prompt"""
        # Simple extraction - look for words after "about" or similar
        patterns = [
            r'about\s+([^.?!]+)',
            r'wikipedia\s+([^.?!]+)',
            r'information\s+on\s+([^.?!]+)',
            r'summary\s+of\s+([^.?!]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                return match.group(1).strip()
        
        # Fallback: use the last few words
        words = prompt.split()
        if len(words) > 2:
            return " ".join(words[-3:])
        
        return "general knowledge"
    
    def _extract_search_query(self, prompt: str) -> str:
        """Extract search query from prompt"""
        # Remove common question words and return the main query
        query = prompt.lower()
        
        # Remove question words
        question_words = ["who", "what", "where", "when", "why", "how", "search", "find"]
        words = query.split()
        filtered_words = [w for w in words if w not in question_words]
        
        return " ".join(filtered_words).strip() or prompt
    
    def _extract_news_topic(self, prompt: str) -> str:
        """Extract news topic from prompt"""
        # Look for words after "news" or similar
        patterns = [
            r'news\s+on\s+([^.?!]+)',
            r'news\s+about\s+([^.?!]+)',
            r'headlines\s+([^.?!]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                return match.group(1).strip()
        
        # Default to general news
        return "general"
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response with embedded tool calls
        This is a simplified version - a real GPT model would use neural networks
        """
        intents = self._detect_intent_and_entities(prompt)
        
        if not intents:
            # Fallback response for unrecognized prompts
            return f"I understand you're asking about: '{prompt}'. Let me search for more information. <tool>search({prompt})</tool>"
        
        response_parts = []
        
        for intent in intents:
            intent_type = intent["type"]
            
            if intent_type in self.response_patterns:
                pattern = random.choice(self.response_patterns[intent_type])
                
                # Fill in the pattern with extracted entities
                if intent_type == "weather" and "city" in intent:
                    response = pattern.format(city=f'"{intent["city"]}"')
                elif intent_type == "crypto" and "symbol" in intent:
                    response = pattern.format(symbol=f'"{intent["symbol"]}"')
                elif intent_type == "wikipedia" and "topic" in intent:
                    response = pattern.format(topic=f'"{intent["topic"]}"')
                elif intent_type == "search" and "query" in intent:
                    response = pattern.format(query=f'"{intent["query"]}"')
                elif intent_type == "news" and "topic" in intent:
                    response = pattern.format(topic=f'"{intent["topic"]}"')
                else:
                    response = pattern.replace("({", "()").replace("})", ")")
                
                response_parts.append(response)
        
        return " ".join(response_parts)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return model information"""
        return {
            "name": self.model_name,
            "temperature": self.temperature,
            "capabilities": [
                "text_generation",
                "tool_calling",
                "context_understanding"
            ]
        }