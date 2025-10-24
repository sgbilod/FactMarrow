# Docker Cagent Guide for FactMarrow

## What is Cagent?

Cagent is Docker's open-source multi-agent runtime that allows you to:
- Define AI agents in simple YAML configuration
- Orchestrate multiple agents with task delegation
- Integrate 50+ Model Context Protocol (MCP) servers
- Deploy agents as reproducible Docker containers
- Share agents via Docker Hub

## Installation

### macOS
```bash
brew install cagent
```

### Linux/Windows
```bash
# Download from releases
curl -L -o cagent https://github.com/docker/cagent/releases/download/v1.0.3/cagent-linux-amd64
chmod +x cagent
sudo mv cagent /usr/local/bin/
```

### Verify
```bash
cagent --version
```

## FactMarrow Configuration

### Main File: `agents/factmarrow_agents.yaml`

This file defines:
- 6 specialized agents (root + 5 sub-agents)
- Each agent's model, instructions, and tools
- MCP server integrations
- Model parameters (temperature, tokens)

### Agent Structure

```yaml
agents:
  root:                          # Agent name
    model: anthropic/claude-sonnet-4-0  # Model to use
    description: "..."
    instruction: |
      Detailed system prompt for this agent
      Explains role, responsibilities, output format
    
    sub_agents:                  # For coordinators
      - agent1
      - agent2
    
    toolsets:                    # External tools
      - type: mcp
        ref: docker:github       # Containerized MCP
      - type: mcp
        command: rust-mcp-filesystem  # Standalone MCP
    
    tools:                       # Built-in tools
      - think              # Complex reasoning
      - memory             # Short-term context
      - todo               # Task management
    
    temperature: 0.2             # Lower = more factual
    context_window: 64000        # Token limit
```

## Running Cagent

### Basic Usage
```bash
# Run with document file
cagent run agents/factmarrow_agents.yaml < document.txt

# Interactive mode (type queries)
cagent run agents/factmarrow_agents.yaml

# With specific config
cagent run agents/factmarrow_agents.yaml --config config/analysis_config.yaml
```

### Environment Variables
```bash
# Set API keys before running
export ANTHROPIC_API_KEY=your_key
export GITHUB_TOKEN=your_token
export GOOGLE_API_KEY=your_key

cagent run agents/factmarrow_agents.yaml
```

## How Multi-Agent Works

1. **Root Agent receives request**
2. **Root Agent analyzes task:**
   - Simple → Handle directly
   - Complex → Delegate to specialist
3. **Specialist agents execute:**
   - Each has specific tools
   - Isolated context
   - Work in parallel or sequence
4. **Root Agent synthesizes results**
5. **Outputs final analysis**

## Tool Integration

### MCP Servers (External Tools)

```yaml
toolsets:
  - type: mcp
    ref: docker:github    # Via Docker MCP Gateway
  
  - type: mcp
    command: rust-mcp-filesystem  # Direct stdio
    args: ["--allow-write", "."]
    tools: ["read_file", "write_file"]  # Specific tools only
```

### Built-in Tools

- **think** - For complex reasoning; outputs reasoning process
- **memory** - Short-term context during conversation
- **todo** - Create task lists for multi-step work

## Debugging

### View Agent Output
```bash
cagent run agents/factmarrow_agents.yaml -v  # Verbose
```

### Test Single Agent
```bash
# Create test_agent.yaml with just one agent
# Then run and debug
cagent run test_agent.yaml
```

### Check Tool Access
Look for permission prompts. Approve to grant tool access.

## Optimization Tips

1. **Temperature Settings:**
   - 0.0 = Deterministic (best for analysis)
   - 0.2-0.5 = Analytical with some creativity
   - 0.7+ = Creative responses

2. **Context Windows:**
   - Longer = More context but slower
   - FactMarrow uses 64K for complex reasoning

3. **Tool Permissions:**
   - Grant only necessary tools per agent
   - Security by principle of least privilege

4. **Agent Delegation:**
   - Let specialists handle their domain
   - Don't overload coordinator

## Sharing Agents

### Push to Docker Hub
```bash
cagent push agents/factmarrow_agents.yaml sgbilod/factmarrow
```

### Pull from Hub
```bash
cagent pull sgbilod/factmarrow
cagent run factmarrow.yaml
```

## Resources

- [Cagent GitHub](https://github.com/docker/cagent)
- [Cagent Documentation](https://docs.docker.com/ai/cagent/)
- [MCP Protocol](https://modelcontextprotocol.io/)
