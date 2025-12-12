#!/usr/bin/env python3
"""
OmniTasker CLI
Command-line interface for OmniTasker automation toolkit
"""
import click
import requests
import json
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()

API_URL = "http://localhost:4000"
TOKEN_FILE = ".omnitasker_token"


def get_token():
    """Get authentication token"""
    try:
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        console.print("[red]Not authenticated. Please login first.[/red]")
        return None


def save_token(token):
    """Save authentication token"""
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)


@click.group()
def cli():
    """OmniTasker CLI - Cross-Platform Automation Toolkit"""
    pass


@cli.command()
@click.option('--username', prompt=True, help='Username')
@click.option('--password', prompt=True, hide_input=True, help='Password')
def login(username, password):
    """Login to OmniTasker"""
    try:
        response = requests.post(f"{API_URL}/api/auth/login", json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            data = response.json()
            save_token(data['token'])
            console.print(f"[green]✓ Logged in as {data['user']['username']}[/green]")
        else:
            console.print(f"[red]✗ Login failed: {response.json().get('error')}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")


@cli.group()
def task():
    """Task management commands"""
    pass


@task.command('list')
def task_list():
    """List all tasks"""
    token = get_token()
    if not token:
        return
    
    try:
        response = requests.get(f"{API_URL}/api/tasks", headers={
            'Authorization': f'Bearer {token}'
        })
        
        if response.status_code == 200:
            tasks = response.json()
            
            if not tasks:
                console.print("[yellow]No tasks found[/yellow]")
                return
            
            table = Table(title="Tasks")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Type", style="blue")
            table.add_column("Status", style="magenta")
            
            for task in tasks:
                table.add_row(
                    task['id'][:8],
                    task['name'],
                    task['script_type'],
                    "Enabled" if task['is_enabled'] else "Disabled"
                )
            
            console.print(table)
        else:
            console.print(f"[red]✗ Failed to fetch tasks[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")


@task.command('run')
@click.argument('task_id')
def task_run(task_id):
    """Execute a task"""
    token = get_token()
    if not token:
        return
    
    try:
        response = requests.post(f"{API_URL}/api/tasks/{task_id}/execute", headers={
            'Authorization': f'Bearer {token}'
        })
        
        if response.status_code == 200:
            data = response.json()
            console.print(f"[green]✓ Task execution initiated[/green]")
            console.print(f"Execution ID: {data['execution']['id']}")
        else:
            console.print(f"[red]✗ Failed to execute task[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")


@cli.group()
def plugin():
    """Plugin management commands"""
    pass


@plugin.command('list')
def plugin_list():
    """List all plugins"""
    token = get_token()
    if not token:
        return
    
    try:
        response = requests.get(f"{API_URL}/api/plugins", headers={
            'Authorization': f'Bearer {token}'
        })
        
        if response.status_code == 200:
            plugins = response.json()
            
            if not plugins:
                console.print("[yellow]No plugins found[/yellow]")
                return
            
            table = Table(title="Plugins")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="blue")
            table.add_column("Version", style="green")
            table.add_column("Status", style="magenta")
            
            for p in plugins:
                table.add_row(
                    p['name'],
                    p['plugin_type'],
                    p['version'],
                    "Enabled" if p['is_enabled'] else "Disabled"
                )
            
            console.print(table)
        else:
            console.print(f"[red]✗ Failed to fetch plugins[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")


@cli.group()
def analytics():
    """Analytics and reporting commands"""
    pass


@analytics.command('overview')
def analytics_overview():
    """Show system overview"""
    token = get_token()
    if not token:
        return
    
    try:
        response = requests.get(f"{API_URL}/api/analytics/overview", headers={
            'Authorization': f'Bearer {token}'
        })
        
        if response.status_code == 200:
            data = response.json()
            
            console.print("\n[bold cyan]System Overview[/bold cyan]")
            console.print(f"Tasks: {data['tasks']['total']} total, {data['tasks']['enabled']} enabled")
            console.print(f"Executions (24h): {data['executions_24h']['total']} total, "
                        f"{data['executions_24h']['successful']} successful, "
                        f"{data['executions_24h']['failed']} failed")
            console.print(f"Plugins: {data['plugins']['total']} total, {data['plugins']['enabled']} enabled\n")
        else:
            console.print(f"[red]✗ Failed to fetch overview[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")


if __name__ == '__main__':
    cli()
