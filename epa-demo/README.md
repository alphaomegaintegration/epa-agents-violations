# EPA Intelligent Compliance System

## 🏛️ Natural Language EPA Water Quality Analysis

A modern web application that combines real EPA data, intelligent AI agents, and natural language processing to analyze water system compliance violations.

### ✨ Features

- **🤖 Natural Language Interface**: Ask questions in plain English
- **🔄 Real-time Agent Updates**: Watch AI agents think and analyze
- **🌐 Real EPA Data**: Integrates with EPA ECHO API
- **📊 Intelligent Analysis**: Three specialized EPA agents
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **☁️ Cloud Ready**: Docker containerized for easy deployment

### 🏗️ Architecture

```
Frontend (React + TypeScript)  ←→  Backend (FastAPI + Python)
         ↕                                    ↕
    WebSocket Updates                 EPA ECHO API
                                     Anthropic API
                                     Agent Intelligence
```

### 🚀 Quick Start

#### Local Development

1. **Clone and setup:**
   ```bash
   cd epa-demo
   cp ../.env .env  # Copy API keys
   ```

2. **Start with Docker:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

#### Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 🎯 Example Questions

Try asking these natural language questions:

- *"What violations does Clinton Machine water system have?"*
- *"Analyze EPA compliance for PWSID OH7700001"*
- *"What public notifications are needed for Springfield water system?"*
- *"Check lead contamination levels for Ohio water systems"*
- *"Show me E.coli violations and health risks"*

### 🤖 EPA Agents

The system employs three intelligent EPA specialists:

1. **🔍 Data Validator**: Verifies EPA data quality and system status
2. **🚨 Violation Analyst**: Analyzes regulatory compliance and violations  
3. **📢 Notification Specialist**: Determines public notification requirements

### 📊 Real Data Sources

- **EPA ECHO API**: Real water system information
- **Laboratory Results**: Actual violation data from CSV files
- **Anthropic API**: AI-powered agent reasoning and analysis

### 🔧 Configuration

Environment variables needed:

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 🚢 EC2 Deployment

1. **Copy project to EC2:**
   ```bash
   scp -r epa-demo/ ec2-user@your-instance:/home/ec2-user/
   ```

2. **Install Docker:**
   ```bash
   sudo yum update -y
   sudo yum install docker -y
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   ```

3. **Install Docker Compose:**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

4. **Deploy:**
   ```bash
   cd epa-demo
   export ANTHROPIC_API_KEY=your_key_here
   docker-compose up -d --build
   ```

5. **Configure security group:**
   - Open ports 3000 (frontend) and 8000 (backend)
   - Access via http://your-ec2-ip:3000

### 📱 API Endpoints

- `POST /analyze` - Analyze natural language EPA questions
- `POST /parse-intent` - Parse question intent and parameters
- `GET /health` - Health check endpoint
- `WS /ws` - WebSocket for real-time updates
- `GET /docs` - Interactive API documentation

### 🔍 Monitoring

- Health checks: `curl http://localhost:8000/health`
- WebSocket status: Check browser developer tools
- Container logs: `docker-compose logs -f`

### 🎨 UI Components

- **QuestionInput**: Natural language question interface
- **AgentPanel**: Real-time agent status and thinking
- **ResultsPanel**: Comprehensive analysis results with tabs

### 🛠️ Tech Stack

**Backend:**
- FastAPI (async Python web framework)
- WebSockets (real-time updates)
- Anthropic API (AI agent reasoning)
- EPA ECHO API (real water system data)

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS (responsive styling)
- Vite (fast development and building)

**Deployment:**
- Docker & Docker Compose
- Nginx (production web server)
- Multi-stage builds (optimized containers)

### 📄 License

Built for EPA compliance demonstration and educational purposes.

### 🤝 Contributing

This is a demonstration system. For production use, consider:
- Rate limiting and authentication
- Enhanced error handling and logging
- Database integration for historical analysis
- Advanced caching strategies
- Security hardening