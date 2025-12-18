# OmniTasker

<div align="center">

![OmniTasker Logo](https://img.shields.io/badge/OmniTasker-Automation%20Toolkit-00f0ff?style=for-the-badge)

**Cross-Platform Automation & AI Toolkit**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-339933?style=flat&logo=node.js&logoColor=white)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

## 🚀 Overview

**OmniTasker** is an enterprise-grade, cross-platform automation and AI toolkit designed to help users automate tasks, analyze data, and manage workflows across Windows, Linux, and macOS. It integrates **8+ programming languages**, provides multiple interfaces (GUI, CLI, Web Dashboard), and supports extensibility through a robust plugin architecture.

### ✨ Key Features

- 🔄 **Multi-OS Automation** - Execute Python, Bash, PowerShell, Lua, and Ruby scripts across different platforms
- 🤖 **AI Integration** - NLP text processing, image classification, and sentiment analysis
- 🔌 **Plugin Architecture** - Extend functionality with Lua and Ruby plugins
- 📊 **Web Dashboard** - Real-time monitoring with futuristic glassmorphism UI
- 💻 **CLI Tool** - Powerful command-line interface for automation management
- ⏰ **Task Scheduling** - Cron-like scheduling with timezone support
- 📧 **Notifications** - Email and Slack integration for task alerts
- 📈 **Analytics** - Comprehensive execution statistics and performance tracking
- 🐳 **Dockerized** - Complete containerization for easy deployment

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     OmniTasker System                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Web Dashboard│  │   CLI Tool   │  │  REST API    │       │
│  │  (React/TS)  │  │   (Python)   │  │  (Node.js)   │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│         ┌──────────────────┴──────────────────┐             │
│         │                                       │           │
│  ┌──────▼───────┐                    ┌─────────▼────────┐   │
│  │   Automation │◄───────────────────┤   PostgreSQL     │   │
│  │    Engine    │                    │    Database      │   │
│  │   (Python)   │                    └──────────────────┘   │
│  └──────┬───────┘                                           │
│         │                                                   │
│    ┌────┴────┬─────────┬──────────┬──────────┐              │
│    │         │         │          │          │              │
│ ┌──▼──┐  ┌──▼──┐  ┌───▼───┐  ┌───▼───┐  ┌──▼──┐             │
│ │ NLP │  │Image│  │Plugin │  │Notify │  │Sched│             │
│ │ AI  │  │ AI  │  │Manager│  │Service│  │uler │             │
│ └─────┘  └─────┘  └───────┘  └───────┘  └─────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

| Component | Technologies |
|-----------|-------------|
| **Core Engine** | Python 3.10+, asyncio, multiprocessing |
| **Backend API** | Node.js 18+, Express, Socket.IO, TypeScript |
| **Frontend** | React 18, TypeScript, SCSS, Recharts |
| **Database** | PostgreSQL 14+ |
| **AI/ML** | Transformers (Hugging Face), OpenCV, scikit-learn |
| **Scripting** | Bash, PowerShell, Lua (lupa), Ruby |
| **Containerization** | Docker, Docker Compose |
| **Authentication** | JWT, bcrypt |
| **Notifications** | SMTP, Slack Webhooks |

## 📦 Installation

### Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for CLI)
- Node.js 18+ (for development)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/OmniTasker.git
   cd OmniTasker
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the dashboard**
   - Web Dashboard: http://localhost:3000
   - API Server: http://localhost:4000
   - Default credentials: `admin` / `admin123`

### Manual Installation

#### Python Automation Engine
```bash
cd automation-engine
pip install -r requirements.txt
python -m src.main
```

#### Node.js API Server
```bash
cd api-server
npm install
npm run dev
```

#### React Web Dashboard
```bash
cd web-dashboard
npm install
npm start
```

#### CLI Tool
```bash
cd cli
pip install -r requirements.txt
chmod +x omnitasker-cli.py
./omnitasker-cli.py --help
```

## 📖 Usage

### Web Dashboard

1. Navigate to http://localhost:3000
2. Login with your credentials
3. Create tasks, manage plugins, and view analytics

### CLI Tool

```bash
# Login
./omnitasker-cli.py login

# List tasks
./omnitasker-cli.py task list

# Execute a task
./omnitasker-cli.py task run <task-id>

# List plugins
./omnitasker-cli.py plugin list

# View analytics
./omnitasker-cli.py analytics overview
```

### Creating a Task

**Via Web Dashboard:**
1. Navigate to Tasks → Create New Task
2. Fill in task details (name, description, script type)
3. Write your automation script
4. Save and execute

**Via API:**
```bash
curl -X POST http://localhost:4000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "System Cleanup",
    "description": "Clean temporary files",
    "script_type": "bash",
    "script_content": "#!/bin/bash\nrm -rf /tmp/*"
  }'
```

### Creating a Plugin

**Lua Plugin Example:**
```lua
-- plugins/examples/my_plugin.lua
function main(args)
    print("Hello from my plugin!")
    return {
        status = "success",
        message = "Plugin executed"
    }
end
```

**Ruby Plugin Example:**
```ruby
# plugins/examples/my_plugin.rb
class MyPlugin
  def execute
    puts "Hello from Ruby plugin!"
    { status: 'success' }
  end
end

MyPlugin.new.execute if __FILE__ == $0
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | localhost |
| `DB_PORT` | PostgreSQL port | 5432 |
| `DB_NAME` | Database name | omnitasker |
| `DB_USER` | Database user | omnitasker |
| `DB_PASSWORD` | Database password | - |
| `JWT_SECRET` | JWT signing secret | - |
| `SMTP_HOST` | Email SMTP host | - |
| `SMTP_PORT` | Email SMTP port | 587 |
| `SLACK_WEBHOOK_URL` | Slack webhook URL | - |

### Scheduling Tasks

Tasks can be scheduled using cron expressions:

```sql
INSERT INTO schedules (task_id, cron_expression, timezone)
VALUES ('task-uuid', '0 0 * * *', 'America/New_York');
```

Cron format: `minute hour day month day_of_week`

## 📊 API Documentation

### Authentication

**POST** `/api/auth/login`
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**POST** `/api/auth/register`
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass"
}
```

### Tasks

- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/:id` - Get task details
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- `POST /api/tasks/:id/execute` - Execute task

### Plugins

- `GET /api/plugins` - List all plugins
- `POST /api/plugins` - Register plugin
- `PUT /api/plugins/:id` - Update plugin
- `DELETE /api/plugins/:id` - Delete plugin

### Analytics

- `GET /api/analytics/overview` - System overview
- `GET /api/analytics/executions` - Execution statistics
- `GET /api/analytics/success-rate` - Task success rates

## 🎨 Screenshots

The web dashboard features a futuristic design with:
- **Glassmorphism effects** - Translucent cards with backdrop blur
- **Neon accents** - Vibrant cyan and magenta highlights
- **Smooth animations** - Hover effects and transitions
- **Dark gradient theme** - Professional dark mode interface
- **Real-time updates** - WebSocket-powered live data

## 🧪 Testing

```bash
# Python tests
cd automation-engine
pytest tests/

# Node.js tests
cd api-server
npm test

# React tests
cd web-dashboard
npm test
```

## 🚀 Deployment

### Production Build

```bash
# Build all services
docker-compose -f docker-compose.yml build

# Start in production mode
NODE_ENV=production BUILD_TARGET=production docker-compose up -d
```

### Environment Setup

1. Update `.env` with production credentials
2. Change default passwords
3. Configure SSL/TLS certificates
4. Set up reverse proxy (nginx/traefik)
5. Enable firewall rules

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hugging Face** - Transformers library for NLP
- **OpenCV** - Image processing capabilities
- **Socket.IO** - Real-time communication
- **React** - Frontend framework
- **Express** - Backend framework

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

<div align="center">

**Built with ❤️ using 8+ programming languages**

[Documentation](docs/) · [Report Bug](issues) · [Request Feature](issues)

</div>
