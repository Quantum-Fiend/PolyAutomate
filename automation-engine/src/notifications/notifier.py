"""
Notification Service
Handles email and Slack notifications
"""
import os
import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Notifier:
    """Handles notifications via email and Slack"""
    
    def __init__(self, db_manager):
        """Initialize notifier"""
        self.db_manager = db_manager
        
        # Email configuration
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        # Slack configuration
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        logger.info("Notifier initialized")
    
    def send_email(self, recipient: str, subject: str, message: str,
                   html: bool = False) -> Dict[str, Any]:
        """
        Send email notification
        
        Args:
            recipient: Email address
            subject: Email subject
            message: Email body
            html: Whether message is HTML
            
        Returns:
            Dict with success status and details
        """
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            logger.warning("Email configuration incomplete, skipping email")
            return {
                'success': False,
                'error': 'Email configuration incomplete'
            }
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Add body
            if html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {recipient}")
            return {
                'success': True,
                'recipient': recipient
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_slack_notification(self, message: str, channel: str = None) -> Dict[str, Any]:
        """
        Send Slack notification via webhook
        
        Args:
            message: Message to send
            channel: Optional channel override
            
        Returns:
            Dict with success status and details
        """
        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured, skipping notification")
            return {
                'success': False,
                'error': 'Slack webhook URL not configured'
            }
        
        try:
            payload = {
                'text': message
            }
            
            if channel:
                payload['channel'] = channel
            
            response = requests.post(
                self.slack_webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Slack notification sent")
                return {
                    'success': True
                }
            else:
                logger.error(f"Slack API error: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Slack API returned {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def notify_task_completion(self, task_name: str, status: str,
                             execution_id: str, recipient: str = None):
        """
        Send notification about task completion
        
        Args:
            task_name: Name of the task
            status: Execution status
            execution_id: UUID of execution
            recipient: Optional email recipient
        """
        # Create message
        emoji = '✅' if status == 'success' else '❌'
        message = f"{emoji} Task '{task_name}' completed with status: {status}\nExecution ID: {execution_id}"
        
        # Send Slack notification
        slack_result = self.send_slack_notification(message)
        
        # Send email if recipient provided
        if recipient:
            email_subject = f"OmniTasker: Task '{task_name}' - {status}"
            email_result = self.send_email(recipient, email_subject, message)
        else:
            email_result = {'success': False, 'error': 'No recipient specified'}
        
        # Log results
        logger.info(f"Notification sent - Slack: {slack_result['success']}, Email: {email_result['success']}")
    
    def notify_task_failure(self, task_name: str, error_message: str,
                          execution_id: str, recipient: str = None):
        """
        Send notification about task failure with error details
        """
        message = f"❌ Task '{task_name}' FAILED\nExecution ID: {execution_id}\nError: {error_message}"
        
        # Send notifications
        self.send_slack_notification(message)
        
        if recipient:
            self.send_email(
                recipient,
                f"OmniTasker: Task '{task_name}' FAILED",
                message
            )
