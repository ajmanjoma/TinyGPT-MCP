"""
Tool Manager - Plugin-ready architecture for dynamic tool management
"""
import asyncio
import importlib
import os
from typing import Dict, Any, List, Optional
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """
    Base class for all tools with plugin architecture
    """
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('tool', '')
        self.enabled = True
        self.category = "general"
        self.version = "1.0.0"
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Any:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get tool description"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get tool parameters schema"""
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate parameters before execution"""
        return True

class ToolManager:
    """
    Advanced tool manager with plugin support and dynamic loading
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.tool_stats: Dict[str, Dict[str, Any]] = {}
        self.plugins_dir = "plugins"
    
    async def initialize(self):
        """Initialize tool manager and load all tools"""
        logger.info("Initializing Tool Manager...")
        
        # Load built-in tools
        await self._load_builtin_tools()
        
        # Load plugin tools
        await self._load_plugin_tools()
        
        logger.info(f"Loaded {len(self.tools)} tools")
    
    async def _load_builtin_tools(self):
        """Load built-in tools"""
        from tools.weather_tool import WeatherTool
        from tools.crypto_tool import CryptoTool
        from tools.wiki_tool import WikiTool
        from tools.search_tool import SearchTool
        from tools.joke_tool import JokeTool
        from tools.news_tool import NewsTool
        
        builtin_tools = [
            WeatherTool(),
            CryptoTool(),
            WikiTool(),
            SearchTool(),
            JokeTool(),
            NewsTool()
        ]
        
        for tool in builtin_tools:
            self.tools[tool.name] = tool
            self.tool_stats[tool.name] = {
                "executions": 0,
                "successes": 0,
                "failures": 0,
                "avg_execution_time": 0.0
            }
    
    async def _load_plugin_tools(self):
        """Load plugin tools dynamically"""
        if not os.path.exists(self.plugins_dir):
            return
        
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                try:
                    module_name = filename[:-3]
                    spec = importlib.util.spec_from_file_location(
                        module_name,
                        os.path.join(self.plugins_dir, filename)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for tool classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BaseTool) and 
                            attr != BaseTool):
                            
                            tool = attr()
                            self.tools[tool.name] = tool
                            self.tool_stats[tool.name] = {
                                "executions": 0,
                                "successes": 0,
                                "failures": 0,
                                "avg_execution_time": 0.0
                            }
                            logger.info(f"Loaded plugin tool: {tool.name}")
                
                except Exception as e:
                    logger.error(f"Failed to load plugin {filename}: {e}")
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Execute a tool with statistics tracking
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        
        if not tool.enabled:
            raise ValueError(f"Tool '{tool_name}' is disabled")
        
        # Validate parameters
        if not tool.validate_params(params):
            raise ValueError(f"Invalid parameters for tool '{tool_name}'")
        
        # Update statistics
        self.tool_stats[tool_name]["executions"] += 1
        
        try:
            import time
            start_time = time.time()
            
            result = await tool.execute(params)
            
            execution_time = time.time() - start_time
            self.tool_stats[tool_name]["successes"] += 1
            
            # Update average execution time
            stats = self.tool_stats[tool_name]
            stats["avg_execution_time"] = (
                (stats["avg_execution_time"] * (stats["successes"] - 1) + execution_time) /
                stats["successes"]
            )
            
            return result
        
        except Exception as e:
            self.tool_stats[tool_name]["failures"] += 1
            logger.error(f"Tool {tool_name} execution failed: {e}")
            raise
    
    def get_available_tools(self) -> List[BaseTool]:
        """Get list of available tools"""
        return list(self.tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a specific tool"""
        return self.tools.get(tool_name)
    
    async def toggle_tool(self, tool_name: str) -> bool:
        """Enable/disable a tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        tool.enabled = not tool.enabled
        
        logger.info(f"Tool {tool_name} {'enabled' if tool.enabled else 'disabled'}")
        return tool.enabled
    
    def get_status(self) -> Dict[str, Any]:
        """Get tool manager status"""
        enabled_tools = sum(1 for tool in self.tools.values() if tool.enabled)
        
        return {
            "total_tools": len(self.tools),
            "enabled_tools": enabled_tools,
            "disabled_tools": len(self.tools) - enabled_tools,
            "tool_stats": self.tool_stats,
            "categories": list(set(tool.category for tool in self.tools.values()))
        }
    
    async def reload_plugins(self):
        """Reload plugin tools"""
        # Remove existing plugin tools
        plugin_tools = [
            name for name, tool in self.tools.items()
            if hasattr(tool, '_is_plugin')
        ]
        
        for tool_name in plugin_tools:
            del self.tools[tool_name]
            del self.tool_stats[tool_name]
        
        # Reload plugins
        await self._load_plugin_tools()
        
        logger.info("Plugin tools reloaded")