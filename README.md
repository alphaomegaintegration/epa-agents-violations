# EPA Intelligent Compliance System

A production-grade EPA compliance intelligence platform combining real government data, current regulatory guidance, and autonomous AI analysis for authentic regulatory decision support.

## 🏛️ Overview

This system provides natural language interface for EPA water quality compliance analysis using real EPA data, AI agents, and current regulatory guidance. It processes actual EPA violations, enforcement actions, and provides comprehensive compliance intelligence briefings.

<img width="397" height="321" alt="ConOps-EPA-RegH2O" src="https://github.com/user-attachments/assets/9e040d1a-cadc-43e6-94c7-60dfec5769fb" />


## 🔧 Architecture

### Data Sources
- **EPA SDWIS API**: Live water system information
- **Real EPA Violations**: Historical violation and enforcement data (201KB JSON)
- **SerpAPI**: Real-time EPA guidance document search
- **Anthropic Claude API**: AI agent reasoning

### AI Agents
1. **Data Validator**: EPA data quality and API validation
2. **Violation Analyst**: Regulatory violations and enforcement analysis
3. **Notification Specialist**: Public notification requirements
4. **Remediation Specialist**: Technical solutions with current EPA guidance

### Multi-Agent System:			
#### Agent Specializations			
Agent	Purpose	Data Sources	Key Functions
Data Validator	Validate EPA data sources	EPA SDWIS API, Historical Data	Validates EPA data sources
Violation Analyst	Analyze compliance violations	Historical Violations, SDWIS	Analyzes violation records
Notification Specialist	Assess notification requirements	EPA Regulations, Violation Data	Assesses notification requirements
Remediation Specialist	Provide technical recommendations	Web Search, Treatment Data	Provides technical recommendations

<img width="723" height="106" alt="image" src="https://github.com/user-attachments/assets/bddd69dc-3550-47be-91fc-48fd67b65d85" />


## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- API Keys:
  - `ANTHROPIC_API_KEY`
  - `SERP_API_KEY`

### Running the System

1. **Clone the repository**
```bash
git clone https://github.com/alphaomegaintegration/epa-agents-violations.git
cd epa-agents-violations
```

2. **Set up environment variables**
```bash
cd epa-demo
cp .env.example .env
# Edit .env with your API keys
```

3. **Start the system**
```bash
docker-compose up --build
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 💡 Usage Examples

### Natural Language Queries
- "What EPA violations does Los Angeles water system have?"
- "Show me compliance issues for Houston water system"
- "What are the notification requirements for Cleveland violations?"

### Supported Water Systems
- Los Angeles (CA1910067) - 3.86M people
- Houston (TX1010013) - 2.2M people  
- Miami-Dade (FL4130871) - 2.3M people
- Cleveland (OH1801212) - 1.3M people
- San Diego (CA3710020) - 1.4M people
- Clinton Machine (OH7700001) - 76 people

## 📊 Features

### Real-Time Intelligence
- Live EPA API integration
- WebSocket agent status updates
- Current EPA guidance search
- Authentic AI reasoning display

### Compliance Analysis
- Actual EPA violation codes
- Enforcement action precedents
- Public notification timelines
- Population impact assessment

### Risk Assessment
- Multi-agent consensus building
- CRITICAL/HIGH/MEDIUM risk classification
- Enforcement precedent analysis
- Immediate action recommendations

## 🏗️ Technical Stack

### Backend
- **FastAPI**: Python web framework
- **Docker**: Containerized deployment
- **WebSockets**: Real-time updates

### Frontend  
- **React + TypeScript**: Modern web interface
- **Tailwind CSS**: Responsive design
- **Vite**: Fast development tooling

### AI & Data
- **Anthropic Claude**: claude-sonnet-4-20250514
- **SerpAPI**: Google search integration
- **EPA SDWIS**: Government compliance data

## 📁 Project Structure

```
epa-demo/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Backend container
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main React app
│   │   └── components/     # React components
│   ├── package.json        # Node dependencies
│   └── Dockerfile         # Frontend container
├── docker-compose.yml      # Full system orchestration
└── real_epa_violations_*.json  # Real EPA data
```

## 🔍 System Flow

1. **Query Processing**: NLP parses natural language questions
2. **Data Retrieval**: Live EPA API + historical violation data
3. **Agent Analysis**: 4 AI agents analyze compliance independently
4. **SerpAPI Enhancement**: Real-time EPA guidance search
5. **Intelligence Synthesis**: Comprehensive briefing generation
6. **Real-Time Response**: WebSocket updates + natural language response

## 📈 Real Data Integration

### EPA Violation Data
- Historical violations from 8 major water systems
- Enforcement action codes (SOX, SFL, SIA, SIE, etc.)
- MCL exceedances and regulatory violations
- Population impact assessments

### Current EPA Guidance
- 2024 regulatory updates
- Treatment technology guidance
- Compliance assistance documents
- Real-time Google search integration

## 🚀 Production Deployment

### AWS EC2 / Production Server Deployment

For production deployment on AWS EC2 or any server with a public IP, see the comprehensive [DEPLOYMENT.md](DEPLOYMENT.md) guide.

**Quick Production Setup:**

1. **Clone and configure**:
```bash
git clone https://github.com/alphaomegaintegration/epa-agents-violations.git
cd epa-agents-violations/epa-demo
cp .env.prod .env
# Edit .env with your EC2 IP and API keys
```

2. **Deploy with production config**:
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

3. **Access your application**:
   - Frontend: `http://YOUR_EC2_IP`
   - Backend API: `http://YOUR_EC2_IP:8000`

**Key Production Changes:**
- Frontend served on port 80 (standard HTTP)
- CORS configured for your domain/IP
- Environment-based API URLs
- Health checks and restart policies
- Production-optimized Docker setup

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions including:
- EC2 setup and security groups
- Environment variable configuration
- SSL/HTTPS setup
- Troubleshooting guide
- Monitoring and maintenance

## 🛡️ Security & Compliance

- Environment variable protection
- API key security
- Docker containerization
- Rate limiting compliance
- Production CORS configuration
- Health monitoring and logging

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request with detailed description

## 📞 Support

For questions or issues, please create a GitHub issue or contact the development team.

---

**EPA Intelligent Compliance System** - Combining real government data with AI intelligence for regulatory compliance analysis.
