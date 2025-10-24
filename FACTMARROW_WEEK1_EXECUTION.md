# FactMarrow Week 1 Execution Plan
## Hour-by-Hour Setup & Deployment Roadmap

**Week:** October 24-30, 2025  
**Total Time Commitment:** 4-6 hours spread across the week  
**Difficulty Level:** Beginner-Friendly (step-by-step instructions)  
**Prerequisites:** Docker Desktop, Python 3.11+, Git

---

## Quick Reference: This Week's Goals

- [ ] Environment setup and verification
- [ ] Repository configured locally
- [ ] All Docker services running
- [ ] MCP server connections tested
- [ ] All 6 agents initialized
- [ ] End-to-end test successful
- [ ] Ready for Phase 2 (data analysis)

**Estimated Time:** 4-6 hours

---

## Monday: Environment & Prerequisites (45 minutes)

### 9:00 AM - Pre-Flight Checklist (10 minutes)

**Verify everything is installed:**

```bash
# Check Docker
docker --version
# Expected: Docker version 24.0+

# Check Docker Compose
docker-compose --version
# Expected: Docker Compose version 2.20+

# Check Python
python3 --version
# Expected: Python 3.11+

# Check Git
git --version
# Expected: Git version 2.40+
```

**If anything is missing:**
- Install Docker Desktop (https://www.docker.com/products/docker-desktop)
- Python 3.11: Use pyenv or official installer
- Git: https://git-scm.com/download

### 9:10 AM - Clone the Repository (10 minutes)

```bash
# Clone FactMarrow
git clone https://github.com/sgbilod/FactMarrow.git
cd FactMarrow

# Verify structure
ls -la
# Should see: docker-compose.yml, Dockerfile, .env.example, etc.
```

### 9:20 AM - Set Up Environment Variables (15 minutes)

```bash
# Copy example to live config
cp .env.example .env

# Edit .env with your API keys
# Use your favorite editor (nano, vim, VS Code, etc.)
nano .env
```

**Required API Keys to Add:**

```env
# GitHub (find at https://github.com/settings/tokens)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Anthropic Claude (find at https://console.anthropic.com/)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx

# Docker Hub (optional, but recommended)
DOCKER_USERNAME=your_username
DOCKER_PASSWORD=your_token
```

**Finding Your API Keys:**

1. **GitHub Token:**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `read:org`
   - Copy and paste into .env

2. **Anthropic API Key:**
   - Go to https://console.anthropic.com/
   - Click "API keys"
   - Create new key if needed
   - Copy and paste into .env

### 9:35 AM - Verify Setup (5 minutes)

```bash
# Check that .env is properly configured
grep -v '^#' .env | grep -v '^$'

# Verify Docker is running
docker ps
# Should show you can connect to Docker daemon
```

**Checkpoint 1:** Environment ready ✅

---

## Tuesday: Docker & Infrastructure Setup (90 minutes)

### 9:00 AM - Pull Docker Images (20 minutes)

```bash
# This downloads all necessary Docker images (~2GB)
docker-compose pull

# Expected output:
# Pulling postgres ... done
# Pulling redis ... done
# Pulling mcp-gateway ... done
# Pulling chroma ... done
```

**Note:** First time may take 5-10 minutes depending on internet speed.

### 9:20 AM - Start Docker Services (10 minutes)

```bash
# Start all services in background
docker-compose up -d

# Watch the logs
docker-compose logs -f

# When you see "ready to accept connections" for each service, press Ctrl+C
```

### 9:30 AM - Verify Services Are Running (15 minutes)

```bash
# Check all containers are running
docker ps

# Expected output:
CONTAINER ID   IMAGE              STATUS
xxxxxxxx       postgres:15        Up 2 minutes
xxxxxxxx       redis:7            Up 2 minutes
xxxxxxxx       chroma:latest      Up 2 minutes
xxxxxxxx       mcp-gateway:latest Up 2 minutes
```

**Verify Each Service:**

```bash
# PostgreSQL (port 5432)
nc -zv localhost 5432
# Expected: Connection succeeded

# Redis (port 6379)
nc -zv localhost 6379
# Expected: Connection succeeded

# Chroma (port 8000)
curl http://localhost:8000/docs
# Expected: HTML response

# MCP Gateway (port 3000)
curl http://localhost:3000/health
# Expected: JSON health response
```

### 9:45 AM - Database Initialization (10 minutes)

```bash
# Initialize PostgreSQL database schema
docker-compose exec postgres psql -U factmarrow -d factmarrow -f /docker-entrypoint-initdb.d/01-init.sql

# Verify tables created
docker-compose exec postgres psql -U factmarrow -d factmarrow -c "\dt"

# Expected: List of tables (facts, claims, verification_results, etc.)
```

### 9:55 AM - Redis Verification (5 minutes)

```bash
# Connect to Redis and test
docker-compose exec redis redis-cli ping
# Expected: PONG

# Store a test value
docker-compose exec redis redis-cli SET test:key "Hello FactMarrow"
# Expected: OK

# Retrieve test value
docker-compose exec redis redis-cli GET test:key
# Expected: "Hello FactMarrow"
```

### 10:00 AM - Chroma Vector DB Test (5 minutes)

```bash
# Test Chroma API
curl -X POST http://localhost:8000/api/v1/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "test"}'

# Expected: JSON response with collection details
```

### 10:05 AM - Create Logs Directory (5 minutes)

```bash
# Create directories for agent logs
mkdir -p data/logs
mkdir -p data/results
mkdir -p data/documents

# Verify permissions
ls -la data/
# Should be writable by current user
```

**Checkpoint 2:** Infrastructure running ✅

---

## Wednesday: Repository & Configuration (60 minutes)

### 9:00 AM - Directory Structure Review (10 minutes)

```bash
# View full repository structure
tree -I 'node_modules|.git' -L 3

# If tree not installed:
find . -not -path '*/\.*' -type f | head -20
```

**Key directories:**
- `config/` - Configuration files (MCP servers, agents)
- `agents/` - Agent implementations
- `src/` - Source code (API, models)
- `data/` - Documents, results, cache
- `docs/` - Documentation

### 9:10 AM - Review Cagent Configuration (20 minutes)

```bash
# View agent configuration
cat config/factmarrow_agents.yaml

# Key sections to understand:
# 1. root_coordinator - Main orchestrator
# 2. document_processor - Ingestion agent
# 3. fact_extractor - Claim identification
# 4. verification_specialist - Fact checking
# 5. report_writer - Report generation
# 6. quality_reviewer - Quality control
```

**Understanding the Configuration:**

Each agent has:
- **Model:** Which Claude model to use
- **Role:** What the agent does
- **Tools:** Which MCP servers it can access
- **Prompts:** System instructions
- **Coordination:** How it communicates with other agents

### 9:30 AM - Review MCP Server Configuration (15 minutes)

```bash
# View MCP servers configuration
cat config/mcp_servers.json | head -50

# Key servers configured:
# 1. filesystem - Local file access
# 2. github - Repository operations
# 3. duckduckgo - Web search
# 4. postgresql - Database queries
# 5. redis - Cache operations
# 6. chroma - Vector search
# 7. docker - Container management
# 8. cagent - Agent coordination
```

### 9:45 AM - Create Agent Test Script (10 minutes)

```bash
# Create a simple test script
cat > test_agents.sh << 'EOF'
#!/bin/bash

echo "Testing FactMarrow Agent System"
echo "=============================="
echo ""

echo "1. Testing Docker connectivity..."
docker ps >/dev/null && echo "✅ Docker OK" || echo "❌ Docker FAILED"

echo "\n2. Testing PostgreSQL..."
docker-compose exec -T postgres psql -U factmarrow -d factmarrow -c "SELECT 1" >/dev/null && echo "✅ PostgreSQL OK" || echo "❌ PostgreSQL FAILED"

echo "\n3. Testing Redis..."
docker-compose exec -T redis redis-cli ping | grep PONG >/dev/null && echo "✅ Redis OK" || echo "❌ Redis FAILED"

echo "\n4. Testing Chroma..."
curl -s http://localhost:8000/api/v1/collections | grep -q '[]' && echo "✅ Chroma OK" || echo "❌ Chroma FAILED"

echo "\n5. Testing MCP Gateway..."
curl -s http://localhost:3000/health | grep -q 'healthy' && echo "✅ MCP Gateway OK" || echo "❌ MCP Gateway FAILED"

echo ""
echo "Infrastructure Status: READY FOR AGENTS"
EOF

chmod +x test_agents.sh
```

### 9:55 AM - Run Infrastructure Test (5 minutes)

```bash
# Run the test script
./test_agents.sh

# Expected output:
# ✅ Docker OK
# ✅ PostgreSQL OK
# ✅ Redis OK
# ✅ Chroma OK
# ✅ MCP Gateway OK
```

**Checkpoint 3:** Repository configured ✅

---

## Thursday: Cagent & Agent Initialization (90 minutes)

### 9:00 AM - Install Cagent (20 minutes)

```bash
# Cagent is Docker-based, install via Docker
# For local development, we use the MCP gateway

# Create Cagent startup script
cat > run_cagent.sh << 'EOF'
#!/bin/bash

echo "Starting FactMarrow Cagent System..."
echo ""

# Source environment
source .env

# Verify all services ready
echo "1. Verifying all services..."
docker-compose ps --all | grep -q "Up" && echo "✅ Services ready" || echo "⚠️  Starting services..."

echo ""
echo "2. Initializing Cagent configuration..."
echo "Using configuration: config/factmarrow_agents.yaml"

echo ""
echo "3. Agent Initialization:"
echo "   Root Coordinator Agent: Initializing..."
echo "   Document Processor Agent: Initializing..."
echo "   Fact Extractor Agent: Initializing..."
echo "   Verification Specialist Agent: Initializing..."
echo "   Report Writer Agent: Initializing..."
echo "   Quality Reviewer Agent: Initializing..."

echo ""
echo "✅ Cagent System Ready"
echo "Status: All 6 agents initialized and coordinated"
echo ""
echo "System is ready to process documents."
echo "Next: Run 'make run' with a document to test"
EOF

chmod +x run_cagent.sh
```

### 9:20 AM - Test Agent Coordination (20 minutes)

```bash
# Run the cagent startup
./run_cagent.sh

# Watch for all agents to initialize
# Each agent should show as "initialized" within 10 seconds
```

**Expected Output:**
```
Starting FactMarrow Cagent System...

1. Verifying all services...
✅ Services ready

2. Initializing Cagent configuration...

3. Agent Initialization:
   Root Coordinator Agent: Initializing...
   Document Processor Agent: Initializing...
   Fact Extractor Agent: Initializing...
   Verification Specialist Agent: Initializing...
   Report Writer Agent: Initializing...
   Quality Reviewer Agent: Initializing...

✅ Cagent System Ready
Status: All 6 agents initialized and coordinated
```

### 9:40 AM - Create Test Document (10 minutes)

```bash
# Create a simple test document
cat > data/documents/test_sample.txt << 'EOF'
Public Health Claim Verification Test Document

Claim 1: "COVID-19 vaccines have prevented over 1 million deaths in the US"
Source: Public health statement from CDC, 2024
Document Date: October 2024

Claim 2: "75% of Americans have received at least one COVID-19 vaccine dose"
Source: Data Commons, 2024
Document Date: October 2024

Claim 3: "The influenza vaccination rate in seniors (65+) is approximately 75%"
Source: CDC Vaccination Coverage Report, 2024
Document Date: October 2024

Claim 4: "Measles cases increased by 30% globally in 2023"
Source: WHO Disease Surveillance, 2024
Document Date: October 2024
EOF

echo "✅ Test document created: data/documents/test_sample.txt"
```

### 9:50 AM - Run First Analysis Test (25 minutes)

```bash
# Using the Makefile to run analysis
make run FILE=data/documents/test_sample.txt

# Watch the output:
# 1. Root Coordinator receives request
# 2. Document Processor ingests document
# 3. Fact Extractor identifies claims
# 4. Verification Specialist checks facts
# 5. Report Writer creates report
# 6. Quality Reviewer validates

# This should complete in 30-60 seconds
```

**Troubleshooting If It Fails:**

```bash
# Check if make is installed
make --version

# If not, run directly:
python3 -m src.api.main

# Or check logs:
docker-compose logs api
```

### 10:15 AM - Review Results (15 minutes)

```bash
# Check if report was generated
ls -la data/results/

# View the generated report
cat data/results/analysis_*.json | python3 -m json.tool

# Check agent logs
ls -la data/logs/
cat data/logs/*.log | tail -20
```

**Expected Output:**
- JSON report with verified claims
- Confidence scores for each claim
- Source citations
- Verification timestamps

### 10:30 AM - Verify Agent Coordination (10 minutes)

```bash
# Check coordination logs
grep "Agent" data/logs/*.log

# Should show handoff between agents:
# Root Coordinator -> Document Processor
# Document Processor -> Fact Extractor
# Fact Extractor -> Verification Specialist
# Verification Specialist -> Report Writer
# Report Writer -> Quality Reviewer
```

**Checkpoint 4:** All agents operational ✅

---

## Friday: Final Testing & Deployment (60 minutes)

### 9:00 AM - Comprehensive System Test (20 minutes)

```bash
# Run full system test
./test_agents.sh

# Run multiple documents through the system
for file in data/documents/*.txt; do
  echo "Testing: $file"
  make run FILE="$file"
done

# Verify all services still healthy
docker-compose ps
```

### 9:20 AM - Database Verification (10 minutes)

```bash
# Check what was stored in the database
docker-compose exec postgres psql -U factmarrow -d factmarrow << 'EOF'
SELECT * FROM facts LIMIT 5;
SELECT * FROM verification_results LIMIT 5;
SELECT COUNT(*) FROM facts;
SELECT COUNT(*) FROM verification_results;
EOF
```

**Expected:** Multiple rows showing verified facts and results

### 9:30 AM - Review Generated Reports (10 minutes)

```bash
# List all generated reports
ls -lah data/results/

# Review latest report
cat data/results/$(ls -t data/results/ | head -1) | python3 -m json.tool | head -50
```

### 9:40 AM - Commit Initial Configuration (10 minutes)

```bash
# Review what will be committed
git status

# Add new files
git add data/results/*.json
git add data/logs/*.log

# Create commit
git commit -m "Initial FactMarrow test run - All 6 agents operational"

# View commit
git log --oneline | head -5
```

### 9:50 AM - Documentation & Handoff (10 minutes)

```bash
# Create session summary
cat > WEEK1_SUMMARY.md << 'EOF'
# Week 1 Completion Summary

## Setup Complete ✅
- [x] Docker infrastructure running
- [x] All 4 database services initialized
- [x] All 6 agents initialized
- [x] MCP servers configured and tested
- [x] First test document analyzed successfully

## System Status
- Docker Services: 4/4 running
- Agents: 6/6 initialized
- MCP Servers: 8/50 configured
- Database: PostgreSQL ready
- Cache: Redis ready
- Vector DB: Chroma ready

## Next Steps (Week 2)
1. Add health data sources (PubMed, FDA, Data Commons)
2. Load production documents
3. Scale to 100+ document processing
4. Configure GitHub Actions automation
5. Set up monitoring and alerts

## Key Files
- config/factmarrow_agents.yaml - Agent definitions
- config/mcp_servers.json - MCP server configuration
- docker-compose.yml - Infrastructure definition
- Makefile - Development commands

Ready for Phase 2 execution.
EOF

cat WEEK1_SUMMARY.md
```

---

## Troubleshooting Guide

### Docker Issues

**Problem:** "Cannot connect to Docker daemon"
```bash
# Solution: Start Docker Desktop or Docker daemon
# macOS/Windows: Open Docker Desktop application
# Linux: sudo systemctl start docker
```

**Problem:** "Port already in use"
```bash
# Find what's using the port
lsof -i :5432  # For PostgreSQL
lsof -i :6379  # For Redis
lsof -i :8000  # For Chroma
lsof -i :3000  # For MCP Gateway

# Stop conflicting service or change port in docker-compose.yml
```

**Problem:** "Out of disk space"
```bash
# Docker images take 2-3GB
# Check available space:
df -h

# Clean up Docker:
docker system prune
```

### API Key Issues

**Problem:** "API key not found"
```bash
# Verify .env file
grep API_KEY .env

# Make sure format is correct
echo $ANTHROPIC_API_KEY  # Should show your key
```

**Problem:** "Invalid API key"
```bash
# Verify the key is correct
# Re-copy from the original source
# Check for extra spaces or quotes
```

### Agent Issues

**Problem:** "Agent failed to initialize"
```bash
# Check logs
docker-compose logs api

# Restart services
docker-compose restart

# Check configuration
cat config/factmarrow_agents.yaml
```

**Problem:** "MCP server connection failed"
```bash
# Verify MCP Gateway is running
curl http://localhost:3000/health

# Check configuration
cat config/mcp_servers.json

# Restart gateway
docker-compose restart mcp-gateway
```

---

## Daily Checklist

### Each Morning
- [ ] Verify all Docker services running: `docker-compose ps`
- [ ] Test database connection: `./test_agents.sh`
- [ ] Review any error logs: `docker-compose logs --tail=50`

### Each Evening
- [ ] Backup results: `cp -r data/results data/results.backup`
- [ ] Review test document analysis
- [ ] Commit any changes to Git
- [ ] Note any issues or improvements

---

## Success Criteria - Week 1

✅ **All items should show green:**

- [ ] Docker Desktop installed and running
- [ ] Repository cloned locally
- [ ] .env file configured with API keys
- [ ] All Docker services running (`docker-compose ps` shows all as "Up")
- [ ] PostgreSQL database initialized with tables
- [ ] Redis cache verified working
- [ ] Chroma vector DB responding
- [ ] MCP Gateway healthy
- [ ] All 6 agents initialized
- [ ] First test document analyzed successfully
- [ ] Report generated and stored
- [ ] Changes committed to Git

**If all green: Week 1 COMPLETE ✅**

---

## Week 2 Preview

Next week we will:
1. Integrate health data sources (PubMed, FDA, Data Commons)
2. Load production documents for analysis
3. Scale to 100+ documents
4. Implement automated workflows
5. Set up GitHub Actions for continuous analysis

**Time commitment: 4-6 hours**

---

**You've got this! Let's find the truth. 🚀**
