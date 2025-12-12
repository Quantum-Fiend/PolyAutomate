"""
OmniTasker Automation Engine
Main entry point for the automation engine service
"""
import os
import sys
import time
import logging
import coloredlogs
from dotenv import load_dotenv

from src.core.scheduler import TaskScheduler
from src.database.db_manager import DatabaseManager
from src.core.task_executor import TaskExecutor

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)
coloredlogs.install(
    level=logging.INFO,
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Main entry point for the automation engine"""
    logger.info("🚀 Starting OmniTasker Automation Engine...")
    
    # Initialize database connection
    try:
        db_manager = DatabaseManager()
        logger.info("✓ Database connection established")
    except Exception as e:
        logger.error(f"✗ Failed to connect to database: {e}")
        sys.exit(1)
    
    # Initialize task executor
    try:
        task_executor = TaskExecutor(db_manager)
        logger.info("✓ Task executor initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize task executor: {e}")
        sys.exit(1)
    
    # Initialize scheduler
    try:
        scheduler = TaskScheduler(db_manager, task_executor)
        logger.info("✓ Task scheduler initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize scheduler: {e}")
        sys.exit(1)
    
    # Start the scheduler in a separate thread
    scheduler.start()
    logger.info("✓ Scheduler started")
    
    logger.info("=" * 60)
    logger.info("OmniTasker Automation Engine is running!")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down gracefully...")
        scheduler.stop()
        db_manager.close()
        logger.info("✓ Shutdown complete")
        sys.exit(0)


if __name__ == "__main__":
    main()
