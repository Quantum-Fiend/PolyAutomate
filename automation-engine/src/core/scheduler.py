"""
Task Scheduler
Handles cron-like scheduling of tasks
"""
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List
from croniter import croniter
import pytz

from src.database.db_manager import DatabaseManager
from src.core.task_executor import TaskExecutor

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled task execution"""
    
    def __init__(self, db_manager: DatabaseManager, task_executor: TaskExecutor):
        """Initialize task scheduler"""
        self.db_manager = db_manager
        self.task_executor = task_executor
        self.running = False
        self.scheduler_thread = None
        self.check_interval = 30  # Check every 30 seconds
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Task scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Task scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                self._check_and_execute_scheduled_tasks()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                self.db_manager.log_system_event(
                    level='error',
                    component='scheduler',
                    message='Scheduler loop error',
                    stack_trace=str(e)
                )
            
            # Sleep for check interval
            time.sleep(self.check_interval)
    
    def _check_and_execute_scheduled_tasks(self):
        """Check for tasks that need to be executed"""
        schedules = self.db_manager.get_active_schedules()
        current_time = datetime.now(pytz.UTC)
        
        for schedule in schedules:
            try:
                # Get timezone
                tz = pytz.timezone(schedule['timezone'])
                
                # If next_run is None, calculate it
                if schedule['next_run'] is None:
                    next_run = self._calculate_next_run(
                        schedule['cron_expression'],
                        current_time,
                        tz
                    )
                    self.db_manager.update_schedule_next_run(schedule['id'], next_run)
                    continue
                
                # Make next_run timezone-aware if it isn't
                next_run = schedule['next_run']
                if next_run.tzinfo is None:
                    next_run = pytz.UTC.localize(next_run)
                
                # Check if it's time to execute
                if current_time >= next_run:
                    logger.info(f"Executing scheduled task: {schedule['task_name']}")
                    
                    # Execute the task
                    self.task_executor.execute_task(
                        task_id=schedule['task_id'],
                        triggered_by='schedule'
                    )
                    
                    # Calculate next run time
                    new_next_run = self._calculate_next_run(
                        schedule['cron_expression'],
                        current_time,
                        tz
                    )
                    
                    # Update schedule
                    self.db_manager.update_schedule_next_run(schedule['id'], new_next_run)
                    
                    logger.info(f"Next run for '{schedule['task_name']}': {new_next_run}")
                    
            except Exception as e:
                logger.error(f"Error processing schedule {schedule['id']}: {e}")
                self.db_manager.log_system_event(
                    level='error',
                    component='scheduler',
                    message=f"Error processing schedule: {schedule['task_name']}",
                    stack_trace=str(e),
                    metadata={'schedule_id': schedule['id']}
                )
    
    def _calculate_next_run(self, cron_expression: str, base_time: datetime, 
                           timezone: pytz.timezone) -> datetime:
        """Calculate the next run time based on cron expression"""
        try:
            # Convert base_time to the schedule's timezone
            local_time = base_time.astimezone(timezone)
            
            # Create croniter instance
            cron = croniter(cron_expression, local_time)
            
            # Get next occurrence
            next_run_local = cron.get_next(datetime)
            
            # Convert back to UTC for storage
            next_run_utc = next_run_local.astimezone(pytz.UTC)
            
            return next_run_utc
            
        except Exception as e:
            logger.error(f"Error calculating next run time: {e}")
            # Default to 1 hour from now if there's an error
            return base_time + timedelta(hours=1)
