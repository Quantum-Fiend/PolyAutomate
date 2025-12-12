"""
Plugin Manager
Handles plugin discovery, loading, and execution
"""
import os
import logging
from typing import Dict, Any, List, Optional
import subprocess

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages plugin lifecycle and execution"""
    
    def __init__(self, db_manager, plugin_dir: str = '/app/plugins'):
        """Initialize plugin manager"""
        self.db_manager = db_manager
        self.plugin_dir = plugin_dir
        self.loaded_plugins = {}
        logger.info(f"Plugin Manager initialized with directory: {plugin_dir}")
    
    def discover_plugins(self) -> List[Dict[str, Any]]:
        """Discover plugins in the plugin directory"""
        discovered = []
        
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory does not exist: {self.plugin_dir}")
            return discovered
        
        for root, dirs, files in os.walk(self.plugin_dir):
            for file in files:
                if file.endswith('.lua') or file.endswith('.rb'):
                    plugin_path = os.path.join(root, file)
                    plugin_type = 'lua' if file.endswith('.lua') else 'ruby'
                    
                    discovered.append({
                        'name': file,
                        'path': plugin_path,
                        'type': plugin_type
                    })
        
        logger.info(f"Discovered {len(discovered)} plugins")
        return discovered
    
    def load_lua_plugin(self, plugin_path: str) -> Optional[Any]:
        """Load a Lua plugin"""
        try:
            from lupa import LuaRuntime
            
            lua = LuaRuntime(unpack_returned_tuples=True)
            
            # Read plugin file
            with open(plugin_path, 'r') as f:
                plugin_code = f.read()
            
            # Execute plugin code
            lua.execute(plugin_code)
            
            logger.info(f"Loaded Lua plugin: {plugin_path}")
            return lua
            
        except Exception as e:
            logger.error(f"Error loading Lua plugin {plugin_path}: {e}")
            return None
    
    def execute_lua_plugin(self, plugin_path: str, function_name: str = 'main',
                          args: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a Lua plugin function
        
        Args:
            plugin_path: Path to Lua plugin file
            function_name: Name of function to execute
            args: Arguments to pass to the function
            
        Returns:
            Dict containing execution results
        """
        try:
            from lupa import LuaRuntime
            
            lua = LuaRuntime(unpack_returned_tuples=True)
            
            # Read and execute plugin
            with open(plugin_path, 'r') as f:
                plugin_code = f.read()
            
            lua.execute(plugin_code)
            
            # Get the function
            func = lua.eval(function_name)
            
            if func is None:
                return {
                    'success': False,
                    'error': f'Function {function_name} not found in plugin'
                }
            
            # Execute function
            if args:
                # Convert Python dict to Lua table
                lua_args = lua.table_from(args)
                result = func(lua_args)
            else:
                result = func()
            
            return {
                'success': True,
                'result': result,
                'plugin_path': plugin_path
            }
            
        except Exception as e:
            logger.error(f"Error executing Lua plugin: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_ruby_plugin(self, plugin_path: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Execute a Ruby plugin
        
        Args:
            plugin_path: Path to Ruby plugin file
            args: Command-line arguments to pass
            
        Returns:
            Dict containing execution results
        """
        try:
            cmd = ['ruby', plugin_path]
            if args:
                cmd.extend(args)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'plugin_path': plugin_path
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Plugin execution timed out (300s)'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'Ruby interpreter not found'
            }
        except Exception as e:
            logger.error(f"Error executing Ruby plugin: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_plugin(self, plugin_id: str, args: Any = None) -> Dict[str, Any]:
        """
        Execute a plugin by its database ID
        
        Args:
            plugin_id: UUID of the plugin
            args: Arguments to pass to the plugin
            
        Returns:
            Dict containing execution results
        """
        # Get plugin from database
        plugins = self.db_manager.get_enabled_plugins()
        plugin = next((p for p in plugins if str(p['id']) == plugin_id), None)
        
        if not plugin:
            return {
                'success': False,
                'error': f'Plugin {plugin_id} not found or disabled'
            }
        
        plugin_path = plugin['file_path']
        plugin_type = plugin['plugin_type']
        
        if plugin_type == 'lua':
            return self.execute_lua_plugin(plugin_path, args=args if isinstance(args, dict) else {})
        elif plugin_type == 'ruby':
            return self.execute_ruby_plugin(plugin_path, args=args if isinstance(args, list) else [])
        else:
            return {
                'success': False,
                'error': f'Unsupported plugin type: {plugin_type}'
            }
    
    def register_plugin(self, name: str, plugin_type: str, file_path: str,
                       description: str = '', version: str = '1.0.0',
                       author: str = '', config: Dict = None) -> bool:
        """
        Register a plugin in the database
        (This would typically be called by the API server)
        """
        # This is a placeholder - actual implementation would use db_manager
        logger.info(f"Registering plugin: {name} ({plugin_type})")
        return True
