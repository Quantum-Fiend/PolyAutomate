"""
Database Manager
Handles all database operations for OmniTasker
"""
import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        """Initialize database connection pool"""
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'omnitasker'),
            'user': os.getenv('DB_USER', 'omnitasker'),
            'password': os.getenv('DB_PASSWORD', 'omnitasker_secure_pass')
        }
        
        # Create connection pool
        self.pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            **self.db_config
        )
        logger.info("Database connection pool created")
    
    def get_connection(self):
        """Get a connection from the pool"""
        return self.pool.getconn()
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        self.pool.putconn(conn)
    
    def close(self):
        """Close all connections in the pool"""
        self.pool.closeall()
        logger.info("Database connections closed")
    
    # ==================== Task Operations ====================
    
    def get_enabled_tasks(self) -> List[Dict[str, Any]]:
        """Get all enabled tasks"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM tasks 
                    WHERE is_enabled = TRUE
                    ORDER BY created_at DESC
                """)
                return [dict(row) for row in cur.fetchall()]
        finally:
            self.return_connection(conn)
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
                result = cur.fetchone()
                return dict(result) if result else None
        finally:
            self.return_connection(conn)
    
    # ==================== Task Execution Operations ====================
    
    def create_task_execution(self, task_id: str, triggered_by: str = 'manual') -> str:
        """Create a new task execution record"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO task_executions (task_id, status, triggered_by)
                    VALUES (%s, 'pending', %s)
                    RETURNING id
                """, (task_id, triggered_by))
                execution_id = cur.fetchone()[0]
                conn.commit()
                return execution_id
        finally:
            self.return_connection(conn)
    
    def update_task_execution_status(self, execution_id: str, status: str):
        """Update task execution status"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE task_executions 
                    SET status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (status, execution_id))
                conn.commit()
        finally:
            self.return_connection(conn)
    
    def complete_task_execution(self, execution_id: str, status: str, 
                               exit_code: int, stdout: str, stderr: str,
                               duration_ms: int, error_message: str = None):
        """Complete a task execution with results"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE task_executions 
                    SET status = %s, 
                        exit_code = %s,
                        stdout = %s,
                        stderr = %s,
                        duration_ms = %s,
                        error_message = %s,
                        completed_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (status, exit_code, stdout, stderr, duration_ms, error_message, execution_id))
                conn.commit()
        finally:
            self.return_connection(conn)
    
    # ==================== Schedule Operations ====================
    
    def get_active_schedules(self) -> List[Dict[str, Any]]:
        """Get all active schedules"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT s.*, t.name as task_name, t.script_type
                    FROM schedules s
                    JOIN tasks t ON s.task_id = t.id
                    WHERE s.is_active = TRUE AND t.is_enabled = TRUE
                """)
                return [dict(row) for row in cur.fetchall()]
        finally:
            self.return_connection(conn)
    
    def update_schedule_next_run(self, schedule_id: str, next_run: datetime):
        """Update the next run time for a schedule"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE schedules 
                    SET next_run = %s, last_run = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (next_run, schedule_id))
                conn.commit()
        finally:
            self.return_connection(conn)
    
    # ==================== Plugin Operations ====================
    
    def get_enabled_plugins(self) -> List[Dict[str, Any]]:
        """Get all enabled plugins"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM plugins 
                    WHERE is_enabled = TRUE
                    ORDER BY name
                """)
                return [dict(row) for row in cur.fetchall()]
        finally:
            self.return_connection(conn)
    
    # ==================== AI Results Operations ====================
    
    def save_ai_result(self, task_execution_id: str, ai_type: str,
                      input_data: str, output_data: Dict[str, Any],
                      confidence_score: float = None, processing_time_ms: int = None,
                      model_name: str = None):
        """Save AI processing results"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ai_results 
                    (task_execution_id, ai_type, input_data, output_data, 
                     confidence_score, processing_time_ms, model_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (task_execution_id, ai_type, input_data, Json(output_data),
                      confidence_score, processing_time_ms, model_name))
                conn.commit()
        finally:
            self.return_connection(conn)
    
    # ==================== Notification Operations ====================
    
    def create_notification(self, task_execution_id: str, notification_type: str,
                          recipient: str, subject: str, message: str):
        """Create a notification record"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO notifications 
                    (task_execution_id, notification_type, recipient, subject, message)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (task_execution_id, notification_type, recipient, subject, message))
                notification_id = cur.fetchone()[0]
                conn.commit()
                return notification_id
        finally:
            self.return_connection(conn)
    
    def update_notification_status(self, notification_id: str, status: str, 
                                   error_message: str = None):
        """Update notification status"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE notifications 
                    SET status = %s, error_message = %s, sent_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (status, error_message, notification_id))
                conn.commit()
        finally:
            self.return_connection(conn)
    
    # ==================== System Logs ====================
    
    def log_system_event(self, level: str, component: str, message: str,
                        stack_trace: str = None, metadata: Dict = None):
        """Log a system event"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO system_logs 
                    (level, component, message, stack_trace, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                """, (level, component, message, stack_trace, Json(metadata or {})))
                conn.commit()
        finally:
            self.return_connection(conn)
