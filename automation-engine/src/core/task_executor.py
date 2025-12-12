"""
Task Executor
Handles execution of tasks across multiple script types
"""
import os
import sys
import logging
import subprocess
import time
import platform
from typing import Dict, Any, Tuple
from datetime import datetime

from src.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Executes tasks and manages their lifecycle"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize task executor"""
        self.db_manager = db_manager
        self.os_type = platform.system()
        logger.info(f"Task executor initialized for {self.os_type}")
    
    def execute_task(self, task_id: str, triggered_by: str = 'manual') -> str:
        """
        Execute a task and return the execution ID
        
        Args:
            task_id: UUID of the task to execute
            triggered_by: Source that triggered the execution
            
        Returns:
            execution_id: UUID of the task execution record
        """
        # Get task details
        task = self.db_manager.get_task_by_id(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return None
        
        if not task['is_enabled']:
            logger.warning(f"Task {task['name']} is disabled")
            return None
        
        # Create execution record
        execution_id = self.db_manager.create_task_execution(task_id, triggered_by)
        logger.info(f"Starting execution {execution_id} for task '{task['name']}'")
        
        # Update status to running
        self.db_manager.update_task_execution_status(execution_id, 'running')
        
        # Execute based on script type
        start_time = time.time()
        
        try:
            if task['script_type'] == 'python':
                exit_code, stdout, stderr = self._execute_python(task)
            elif task['script_type'] == 'bash':
                exit_code, stdout, stderr = self._execute_bash(task)
            elif task['script_type'] == 'powershell':
                exit_code, stdout, stderr = self._execute_powershell(task)
            elif task['script_type'] == 'lua':
                exit_code, stdout, stderr = self._execute_lua(task)
            elif task['script_type'] == 'ruby':
                exit_code, stdout, stderr = self._execute_ruby(task)
            else:
                raise ValueError(f"Unsupported script type: {task['script_type']}")
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Determine status based on exit code
            status = 'success' if exit_code == 0 else 'failed'
            error_message = stderr if exit_code != 0 else None
            
            # Update execution record
            self.db_manager.complete_task_execution(
                execution_id=execution_id,
                status=status,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_ms=duration_ms,
                error_message=error_message
            )
            
            logger.info(f"Task '{task['name']}' completed with status: {status} (duration: {duration_ms}ms)")
            
            return execution_id
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_message = str(e)
            
            self.db_manager.complete_task_execution(
                execution_id=execution_id,
                status='failed',
                exit_code=-1,
                stdout='',
                stderr=error_message,
                duration_ms=duration_ms,
                error_message=error_message
            )
            
            logger.error(f"Task '{task['name']}' failed: {error_message}")
            
            # Log to system logs
            self.db_manager.log_system_event(
                level='error',
                component='task_executor',
                message=f"Task execution failed: {task['name']}",
                stack_trace=error_message,
                metadata={'task_id': task_id, 'execution_id': execution_id}
            )
            
            return execution_id
    
    def _execute_python(self, task: Dict[str, Any]) -> Tuple[int, str, str]:
        """Execute Python script"""
        script_content = task['script_content']
        
        # Create temporary script file
        script_path = f"/tmp/omnitasker_python_{task['id']}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        finally:
            # Clean up temporary file
            if os.path.exists(script_path):
                os.remove(script_path)
    
    def _execute_bash(self, task: Dict[str, Any]) -> Tuple[int, str, str]:
        """Execute Bash script"""
        if self.os_type == 'Windows':
            logger.warning("Bash scripts not natively supported on Windows")
            return -1, '', 'Bash not supported on Windows'
        
        script_content = task['script_content']
        
        # Create temporary script file
        script_path = f"/tmp/omnitasker_bash_{task['id']}.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        try:
            result = subprocess.run(
                ['/bin/bash', script_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout, result.stderr
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)
    
    def _execute_powershell(self, task: Dict[str, Any]) -> Tuple[int, str, str]:
        """Execute PowerShell script"""
        script_content = task['script_content']
        
        # Determine PowerShell executable
        if self.os_type == 'Windows':
            ps_executable = 'powershell.exe'
        else:
            ps_executable = 'pwsh'  # PowerShell Core for Linux/macOS
        
        # Create temporary script file
        script_path = f"/tmp/omnitasker_ps_{task['id']}.ps1"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        try:
            result = subprocess.run(
                [ps_executable, '-ExecutionPolicy', 'Bypass', '-File', script_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError:
            return -1, '', f'{ps_executable} not found on system'
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)
    
    def _execute_lua(self, task: Dict[str, Any]) -> Tuple[int, str, str]:
        """Execute Lua script using lupa"""
        try:
            from lupa import LuaRuntime
            
            lua = LuaRuntime(unpack_returned_tuples=True)
            script_content = task['script_content']
            
            # Capture output
            output = []
            
            # Override print function to capture output
            lua.execute("""
                original_print = print
                print = function(...)
                    local args = {...}
                    for i, v in ipairs(args) do
                        table.insert(output_buffer, tostring(v))
                    end
                end
                output_buffer = {}
            """)
            
            # Execute the script
            lua.execute(script_content)
            
            # Get output
            output_buffer = lua.eval('output_buffer')
            stdout = '\n'.join([str(item) for item in output_buffer])
            
            return 0, stdout, ''
            
        except Exception as e:
            return -1, '', str(e)
    
    def _execute_ruby(self, task: Dict[str, Any]) -> Tuple[int, str, str]:
        """Execute Ruby script"""
        script_content = task['script_content']
        
        # Create temporary script file
        script_path = f"/tmp/omnitasker_ruby_{task['id']}.rb"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        try:
            result = subprocess.run(
                ['ruby', script_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError:
            return -1, '', 'Ruby not found on system'
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)
