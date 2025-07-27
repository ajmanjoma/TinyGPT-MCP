"""
TinyGPT Model Implementation
Lightweight GPT-style model with intelligent intent detection
"""
import asyncio
import time
import json
from typing import Dict, Any, List, Optional
import logging
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

logger = logging.getLogger(__name__)

class TinyGPTModel:
    """
    Lightweight GPT model with tool-calling capabilities
    Uses DistilGPT-2 for fast inference with custom prompt engineering
    """
    
    def __init__(self, model_name: str = "distilgpt2"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Tool detection patterns
        self.tool_patterns = {
            "weather": ["weather", "temperature", "forecast", "climate", "rain", "sunny", "cloudy"],
            "crypto": ["price", "crypto", "bitcoin", "ethereum", "btc", "eth", "coin", "cryptocurrency"],
            "wiki": ["wikipedia", "wiki", "information about", "tell me about", "summary", "explain"],
            "search": ["search", "find", "look up", "who won", "latest", "recent", "google"],
            "joke": ["joke", "funny", "humor", "laugh", "amusing", "comedy"],
            "news": ["news", "headlines", "current events", "breaking", "latest news"]
        }
    
    async def initialize(self):
        """Initialize the model and tokenizer"""
        try:
            logger.info(f"Loading TinyGPT model: {self.model_name}")
            
            # Load tokenizer
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            logger.info(f"TinyGPT model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load TinyGPT model: {e}")
            # Fallback to pattern-based responses
            self.is_loaded = False
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response with tool calling capabilities
        """
        start_time = time.time()
        
        try:
            # Detect intents and generate tool calls
            detected_tools = self._detect_tools(prompt)
            
            if self.is_loaded and self.model:
                # Use actual model for text generation
                response_text = await self._generate_with_model(
                    prompt, temperature, max_tokens, detected_tools
                )
            else:
                # Use pattern-based fallback
                response_text = self._generate_pattern_response(prompt, detected_tools)
            
            tokens_used = len(self.tokenizer.encode(response_text)) if self.tokenizer else len(response_text.split())
            
            return {
                "text": response_text,
                "model_info": {
                    "name": f"TinyGPT-{self.model_name}",
                    "device": self.device,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                "tokens_used": tokens_used,
                "generation_time": time.time() - start_time,
                "detected_tools": detected_tools
            }
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {
                "text": f"I apologize, but I encountered an error processing your request. Let me search for information to help you. <tool>search</tool>",
                "model_info": {"name": "TinyGPT-fallback", "error": str(e)},
                "tokens_used": 0,
                "generation_time": time.time() - start_time,
                "detected_tools": ["search"]
            }
    
    def _detect_tools(self, prompt: str) -> List[str]:
        """
        Detect which tools should be called based on the prompt
        """
        prompt_lower = prompt.lower()
        detected = []
        
        for tool, keywords in self.tool_patterns.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected.append(tool)
        
        # If no specific tools detected, default to search
        if not detected:
            detected.append("search")
        
        return detected
    
    async def _generate_with_model(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        detected_tools: List[str]
    ) -> str:
        """
        Generate response using the actual GPT model
        """
        try:
            # Create enhanced prompt with tool awareness
            enhanced_prompt = self._create_tool_aware_prompt(prompt, detected_tools)
            
            # Tokenize
            inputs = self.tokenizer.encode(enhanced_prompt, return_tensors="pt").to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    attention_mask=torch.ones_like(inputs)
                )
            
            # Decode response
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the new part (remove the prompt)
            response = generated_text[len(enhanced_prompt):].strip()
            
            # Add tool calls if not present
            if not any(f"<tool>{tool}" in response for tool in detected_tools):
                response = self._add_tool_calls(response, detected_tools)
            
            return response
            
        except Exception as e:
            logger.error(f"Model generation error: {e}")
            return self._generate_pattern_response(prompt, detected_tools)
    
    def _create_tool_aware_prompt(self, prompt: str, detected_tools: List[str]) -> str:
        """
        Create a prompt that encourages tool usage
        """
        tool_descriptions = {
            "weather": "use <tool>weather</tool> to get weather information",
            "crypto": "use <tool>crypto</tool> to get cryptocurrency prices",
            "wiki": "use <tool>wiki</tool> to get Wikipedia information",
            "search": "use <tool>search</tool> to search for information",
            "joke": "use <tool>joke</tool> to get a joke",
            "news": "use <tool>news</tool> to get news"
        }
        
        available_tools = ", ".join([tool_descriptions.get(tool, tool) for tool in detected_tools])
        
        enhanced_prompt = f"""You are TinyGPT, an AI assistant with access to tools. When users ask questions, you can {available_tools}.

User: {prompt}
Assistant: I'll help you with that."""
        
        return enhanced_prompt
    
    def _generate_pattern_response(self, prompt: str, detected_tools: List[str]) -> str:
        """
        Generate response using pattern matching (fallback)
        """
        responses = {
            "weather": "Let me check the weather information for you. <tool>weather</tool>",
            "crypto": "I'll get the latest cryptocurrency prices. <tool>crypto</tool>",
            "wiki": "Let me search Wikipedia for that information. <tool>wiki</tool>",
            "search": "I'll search for the latest information on that. <tool>search</tool>",
            "joke": "Here's a joke for you! <tool>joke</tool>",
            "news": "Let me get the latest news on that topic. <tool>news</tool>"
        }
        
        if len(detected_tools) == 1:
            return responses.get(detected_tools[0], "Let me help you with that. <tool>search</tool>")
        
        # Multiple tools
        tool_calls = " ".join([f"<tool>{tool}</tool>" for tool in detected_tools])
        return f"I'll help you with that by using multiple tools. {tool_calls}"
    
    def _add_tool_calls(self, response: str, detected_tools: List[str]) -> str:
        """
        Add tool calls to response if missing
        """
        for tool in detected_tools:
            if f"<tool>{tool}" not in response:
                response += f" <tool>{tool}</tool>"
        
        return response
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get model status information
        """
        return {
            "model_name": self.model_name,
            "is_loaded": self.is_loaded,
            "device": self.device,
            "available_tools": list(self.tool_patterns.keys()),
            "memory_usage": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        }