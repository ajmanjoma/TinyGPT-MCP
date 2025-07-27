"""
Model Context Protocol (MCP) Engine
Handles parsing and execution of tool calls with advanced orchestration
"""
import re
import json
import asyncio
import time
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class MCPEngine:
    """
    Advanced MCP engine with concurrent tool execution and error handling
    """
    
    def __init__(self, tool_manager):
        self.tool_manager = tool_manager
        self.tool_pattern = r'<tool>(\w+)(?:\(([^)]*)\))?</tool>'
        self.max_concurrent_tools = 5
        self.tool_timeout = 30.0
    
    async def process_response(
        self,
        model_response: str,
        available_tools: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process model response and execute tool calls
        """
        try:
            # Parse tool calls from response
            tool_calls = self._parse_tool_calls(model_response)
            
            # Filter by available tools if specified
            if available_tools:
                tool_calls = [
                    call for call in tool_calls 
                    if call["tool"] in available_tools
                ]
            
            if not tool_calls:
                return []
            
            logger.info(f"Executing {len(tool_calls)} tool calls")
            
            # Execute tools concurrently with timeout
            results = await self._execute_tools_concurrent(tool_calls)
            
            return results
            
        except Exception as e:
            logger.error(f"MCP processing error: {e}")
            return []
    
    def _parse_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse tool calls from model response
        Enhanced parsing with parameter extraction
        """
        tool_calls = []
        matches = re.findall(self.tool_pattern, text)
        
        for match in matches:
            tool_name = match[0]
            params_str = match[1] if len(match) > 1 else ""
            
            # Parse parameters
            params = self._parse_parameters(params_str, tool_name)
            
            tool_calls.append({
                "tool": tool_name,
                "params": params,
                "raw_call": f"<tool>{tool_name}({params_str})</tool>"
            })
        
        return tool_calls
    
    def _parse_parameters(self, params_str: str, tool_name: str) -> Dict[str, Any]:
        """
        Parse tool parameters with intelligent defaults
        """
        params = {}
        
        if not params_str.strip():
            return self._get_default_params(tool_name)
        
        try:
            # Try JSON parsing first
            if params_str.startswith('{') and params_str.endswith('}'):
                params = json.loads(params_str)
            else:
                # Simple key=value or positional parsing
                if '=' in params_str:
                    # Named parameters
                    pairs = params_str.split(',')
                    for pair in pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            params[key.strip()] = value.strip().strip('"\'')
                else:
                    # Positional parameter
                    value = params_str.strip().strip('"\'')
                    params = self._map_positional_param(tool_name, value)
        
        except Exception as e:
            logger.warning(f"Parameter parsing error for {tool_name}: {e}")
            params = self._get_default_params(tool_name)
        
        return params
    
    def _get_default_params(self, tool_name: str) -> Dict[str, Any]:
        """
        Get default parameters for tools
        """
        defaults = {
            "weather": {"location": "London"},
            "crypto": {"symbol": "bitcoin"},
            "wiki": {"topic": "artificial intelligence"},
            "search": {"query": "latest news"},
            "joke": {},
            "news": {"topic": "technology"}
        }
        
        return defaults.get(tool_name, {})
    
    def _map_positional_param(self, tool_name: str, value: str) -> Dict[str, Any]:
        """
        Map positional parameters to named parameters
        """
        mappings = {
            "weather": {"location": value},
            "crypto": {"symbol": value},
            "wiki": {"topic": value},
            "search": {"query": value},
            "news": {"topic": value},
            "joke": {}
        }
        
        return mappings.get(tool_name, {"query": value})
    
    async def _execute_tools_concurrent(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tools concurrently with proper error handling
        """
        # Limit concurrent executions
        semaphore = asyncio.Semaphore(self.max_concurrent_tools)
        
        async def execute_single_tool(tool_call):
            async with semaphore:
                return await self._execute_single_tool(tool_call)
        
        # Execute all tools concurrently
        tasks = [execute_single_tool(call) for call in tool_calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    **tool_calls[i],
                    "result": f"Tool execution failed: {str(result)}",
                    "success": False,
                    "execution_time": 0.0,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_single_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single tool with timeout and error handling
        """
        start_time = time.time()
        tool_name = tool_call["tool"]
        params = tool_call["params"]
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self.tool_manager.execute_tool(tool_name, params),
                timeout=self.tool_timeout
            )
            
            execution_time = time.time() - start_time
            
            return {
                **tool_call,
                "result": result,
                "success": True,
                "execution_time": execution_time
            }
        
        except asyncio.TimeoutError:
            return {
                **tool_call,
                "result": f"Tool execution timed out after {self.tool_timeout}s",
                "success": False,
                "execution_time": self.tool_timeout,
                "error": "timeout"
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tool {tool_name} execution error: {e}")
            
            return {
                **tool_call,
                "result": f"Tool execution error: {str(e)}",
                "success": False,
                "execution_time": execution_time,
                "error": str(e)
            }
    
    async def format_final_response(
        self,
        original_response: str,
        tool_calls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Format the final response by integrating tool results
        """
        # Extract thought process (text before first tool call)
        thought = self._extract_thought(original_response)
        
        # Replace tool calls with results in the response
        final_answer = original_response
        
        for tool_call in tool_calls:
            if tool_call["success"]:
                replacement = self._format_tool_result(tool_call)
                final_answer = final_answer.replace(
                    tool_call["raw_call"],
                    replacement
                )
            else:
                final_answer = final_answer.replace(
                    tool_call["raw_call"],
                    f"[Error: {tool_call['result']}]"
                )
        
        return {
            "thought": thought,
            "final_answer": final_answer,
            "tool_summary": self._create_tool_summary(tool_calls)
        }
    
    def _extract_thought(self, response: str) -> str:
        """
        Extract the thinking process before tool calls
        """
        match = re.search(self.tool_pattern, response)
        if match:
            thought = response[:match.start()].strip()
            return thought if thought else "Let me help you with that."
        
        return response
    
    def _format_tool_result(self, tool_call: Dict[str, Any]) -> str:
        """
        Format tool result for integration into final response
        """
        tool_name = tool_call["tool"]
        result = tool_call["result"]
        
        if isinstance(result, dict):
            # Format structured results
            if tool_name == "weather":
                return f"Weather: {result.get('description', 'N/A')}, {result.get('temperature', 'N/A')}"
            elif tool_name == "crypto":
                return f"Price: {result.get('price', 'N/A')}"
            else:
                return str(result)
        
        return str(result)
    
    def _create_tool_summary(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a summary of tool executions
        """
        successful = sum(1 for call in tool_calls if call["success"])
        failed = len(tool_calls) - successful
        total_time = sum(call["execution_time"] for call in tool_calls)
        
        return {
            "total_tools": len(tool_calls),
            "successful": successful,
            "failed": failed,
            "total_execution_time": round(total_time, 3),
            "tools_used": [call["tool"] for call in tool_calls]
        }