"""
Model Context Protocol (MCP) Engine
Handles parsing and execution of tool calls from TinyGPT responses
"""
import re
import json
from typing import List, Dict, Any, Optional
from tools import ToolRegistry

class MCPEngine:
    """
    Handles the Model Context Protocol for tool calling
    Format: <tool>function_name(arguments)</tool>
    """
    
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.tool_call_pattern = r'<tool>(\w+)\(([^)]*)\)</tool>'
    
    def parse_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse tool calls from TinyGPT output
        Returns list of tool call dictionaries
        """
        tool_calls = []
        matches = re.findall(self.tool_call_pattern, text)
        
        for match in matches:
            function_name = match[0]
            args_string = match[1]
            
            # Parse arguments
            try:
                # Handle quoted arguments
                if args_string.strip():
                    # Simple argument parsing - in production, use a proper parser
                    args = self._parse_arguments(args_string)
                else:
                    args = {}
                
                tool_calls.append({
                    "function": function_name,
                    "arguments": args,
                    "raw_call": f"<tool>{function_name}({args_string})</tool>"
                })
            except Exception as e:
                print(f"Error parsing tool call arguments: {e}")
                continue
        
        return tool_calls
    
    def _parse_arguments(self, args_string: str) -> Dict[str, Any]:
        """Parse function arguments from string"""
        args = {}
        
        # Remove quotes and split by comma if multiple args
        cleaned_args = args_string.strip().strip('"\'')
        
        if not cleaned_args:
            return args
        
        # For now, assume single argument functions
        # In production, implement proper argument parsing
        if '=' in cleaned_args:
            # Named arguments: key=value
            pairs = cleaned_args.split(',')
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    args[key.strip()] = value.strip().strip('"\'')
        else:
            # Positional argument - map to first parameter of function
            args['query'] = cleaned_args  # Default parameter name
        
        return args
    
    async def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute all tool calls and return results
        """
        results = []
        
        for tool_call in tool_calls:
            function_name = tool_call["function"]
            arguments = tool_call["arguments"]
            
            try:
                # Execute the tool
                result = await self.tool_registry.execute_tool(function_name, arguments)
                
                results.append({
                    "function": function_name,
                    "arguments": arguments,
                    "result": result,
                    "success": True,
                    "raw_call": tool_call["raw_call"]
                })
            
            except Exception as e:
                results.append({
                    "function": function_name,
                    "arguments": arguments,
                    "result": f"Error: {str(e)}",
                    "success": False,
                    "raw_call": tool_call["raw_call"]
                })
        
        return results
    
    def format_final_response(self, original_response: str, tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format the final response by replacing tool calls with results
        """
        # Start with the original response
        final_text = original_response
        
        # Replace each tool call with its result
        for result in tool_results:
            if result["success"]:
                replacement = self._format_tool_result(result)
                final_text = final_text.replace(result["raw_call"], replacement)
            else:
                final_text = final_text.replace(result["raw_call"], f"[Error: {result['result']}]")
        
        return {
            "thought": self._extract_thought(original_response),
            "tool_calls": tool_results,
            "final_answer": final_text,
            "raw_response": original_response
        }
    
    def _extract_thought(self, response: str) -> str:
        """Extract the thinking part before tool calls"""
        # Find the first tool call
        match = re.search(self.tool_call_pattern, response)
        if match:
            thought = response[:match.start()].strip()
            return thought if thought else "Let me help you with that."
        
        return response
    
    def _format_tool_result(self, result: Dict[str, Any]) -> str:
        """Format tool result for inclusion in final response"""
        function_name = result["function"]
        tool_result = result["result"]
        
        # Format based on tool type
        if function_name == "weather":
            if isinstance(tool_result, dict) and "temperature" in str(tool_result):
                return f"The weather information: {tool_result}"
            return str(tool_result)
        
        elif function_name == "crypto_price":
            if isinstance(tool_result, dict):
                return f"Current price: {tool_result}"
            return str(tool_result)
        
        elif function_name == "wiki":
            return f"Wikipedia summary: {tool_result}"
        
        elif function_name == "search":
            return f"Search results: {tool_result}"
        
        elif function_name == "joke":
            return str(tool_result)
        
        elif function_name == "news":
            return f"Latest news: {tool_result}"
        
        else:
            return str(tool_result)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools"""
        return self.tool_registry.get_tool_descriptions()