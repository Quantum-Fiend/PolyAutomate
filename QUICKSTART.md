# OmniTasker - Quick Start Guide

## Prerequisites

- Docker Desktop installed and running
- 8GB RAM minimum
- 10GB free disk space

## Installation Steps

### 1. Clone or Download

Download the OmniTasker project to your local machine.

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

**Minimum required configuration:**
```env
DB_PASSWORD=your_secure_password_here
JWT_SECRET=your_jwt_secret_key_here
```

**Optional (for notifications):**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Python automation engine
- Node.js API server (port 4000)
- React web dashboard (port 3000)

### 4. Verify Installation

Check that all containers are running:
```bash
docker-compose ps
```

You should see 4 services running:
- `omnitasker-db`
- `omnitasker-engine`
- `omnitasker-api`
- `omnitasker-web`

### 5. Access the Dashboard

Open your browser and navigate to:
```
http://localhost:3000
```

**Default credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **IMPORTANT:** Change the default password immediately after first login!

## First Steps

### 1. Create Your First Task

1. Navigate to **Tasks** in the sidebar
2. Click **Create New Task**
3. Fill in the details:
   - **Name:** "Hello World"
   - **Description:** "My first automation task"
   - **Script Type:** Python
   - **Script Content:**
     ```python
     print("Hello from OmniTasker!")
     print("Task executed successfully")
     ```
4. Click **Save**
5. Click **Execute** to run the task

### 2. View Execution Results

1. Navigate to **Analytics**
2. View execution statistics and charts
3. Check the dashboard for real-time updates

### 3. Install a Plugin

Sample plugins are located in `plugins/examples/`:
- `hello_world.lua` - Simple Lua plugin
- `file_watcher.rb` - Ruby file monitoring plugin

To register a plugin via API:
```bash
curl -X POST http://localhost:4000/api/plugins \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hello World",
    "description": "Sample Lua plugin",
    "plugin_type": "lua",
    "version": "1.0.0",
    "file_path": "/app/plugins/examples/hello_world.lua"
  }'
```

## Using the CLI

### Install CLI Dependencies

```bash
cd cli
pip install -r requirements.txt
```

### Login

```bash
python omnitasker-cli.py login
```

### List Tasks

```bash
python omnitasker-cli.py task list
```

### Execute a Task

```bash
python omnitasker-cli.py task run <task-id>
```

### View System Overview

```bash
python omnitasker-cli.py analytics overview
```

## Troubleshooting

### Services Not Starting

Check logs:
```bash
docker-compose logs -f
```

### Database Connection Issues

Ensure PostgreSQL is healthy:
```bash
docker-compose logs postgres
```

### Port Conflicts

If ports 3000, 4000, or 5432 are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change 3000 to 3001
```

### Reset Everything

Stop and remove all containers:
```bash
docker-compose down -v
docker-compose up -d
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [API Documentation](docs/API.md)
- Learn about [Plugin Development](docs/PLUGIN_DEVELOPMENT.md)
- Check [Deployment Guide](docs/DEPLOYMENT.md) for production setup

## Support

For issues or questions:
1. Check the documentation
2. Review existing GitHub issues
3. Create a new issue with detailed information

---

**Happy Automating! 🚀**
