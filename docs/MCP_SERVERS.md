# MCP Servers in FactMarrow

## Model Context Protocol Overview

MCP is an open standard for AI assistants to communicate with external tools and data sources. FactMarrow integrates 50+ MCP servers for enhanced capabilities.

## Currently Integrated Servers

### Tier 1: Core (Docker MCP Gateway)

#### GitHub MCP
- **Purpose:** Repository and issue management
- **Reference:** `docker:github`
- **Tools:**
  - `read_repository` - Get repo metadata
  - `search_code` - Search repository code
  - `create_issue` - Create analysis issues
  - `update_issue` - Update issue status
  - `list_issues` - Get analysis queue
  - `create_pull_request` - Propose changes
- **Use in FactMarrow:** Track analyses, publish reports

#### DuckDuckGo Search MCP
- **Purpose:** Privacy-respecting web search
- **Reference:** `docker:duckduckgo`
- **Tools:**
  - `search` - Web search queries
  - `instant_answer` - Direct answers
- **Use in FactMarrow:** Fact verification, finding supporting evidence

#### Filesystem MCP
- **Purpose:** Secure local file operations
- **Reference:** `rust-mcp-filesystem`
- **Tools:**
  - `read_file` - Read document contents
  - `write_file` - Save analysis results
  - `list_directory` - Navigate file system
- **Use in FactMarrow:** Document processing, result storage

### Tier 2: Data & Search

#### Data Commons MCP (NEW Oct 2025)
- **Purpose:** Access 30M+ public health data points
- **Reference:** `data_commons_mcp`
- **Data Available:**
  - Disease statistics by region
  - Health outcomes and metrics
  - Economic health correlations
  - Vaccination data
  - Mortality statistics
- **Use in FactMarrow:** Verify health claims against authoritative data

#### PubMed API
- **Purpose:** Access peer-reviewed medical research
- **Free Tier:** Yes
- **Tools:**
  - Full-text search
  - Abstract retrieval
  - Citation metadata
- **Use in FactMarrow:** Find supporting research for claims

#### FDA API
- **Purpose:** Drug and device approval data
- **Free Tier:** Yes
- **Data Available:**
  - Drug approvals and recalls
  - Adverse event reports
  - Device classifications
  - Enforcement actions
- **Use in FactMarrow:** Verify pharmaceutical claims

### Tier 3: Vector & Semantic Search

#### Chroma MCP
- **Purpose:** Vector database for semantic search
- **Deployment:** Local or cloud
- **Capabilities:**
  - Document embedding
  - Similarity search
  - Semantic clustering
- **Use in FactMarrow:** Find similar past analyses

#### Vectara MCP
- **Purpose:** Commercial RAG solution
- **Free Tier:** Limited
- **Capabilities:**
  - Context-aware retrieval
  - Domain-specific embeddings
  - Custom indexing

### Tier 4: Workflow & Integration

#### Slack MCP
- **Purpose:** Team notifications
- **Notifications:** Analysis updates, results
- **Use in FactMarrow:** Real-time team alerts

#### Notion MCP
- **Purpose:** Knowledge base integration
- **Use in FactMarrow:** Archive of past analyses

#### Google Drive MCP
- **Purpose:** Document storage and sharing
- **Use in FactMarrow:** Collaborative analysis workspace

## Adding New MCP Servers

### Configuration

1. **Update `config/mcp_servers.yaml`:**
```yaml
mcp_servers:
  new_server:
    type: "stdio|http|sse"
    command: "command-name"
    auth:
      token: ${API_TOKEN}
```

2. **Update agent in `agents/factmarrow_agents.yaml`:**
```yaml
toolsets:
  - type: mcp
    command: new-server
    tools: ["tool1", "tool2"]
```

3. **Test integration:**
```bash
cagent run agents/factmarrow_agents.yaml
```

4. **Document in this file**

## Free Resources

**All MCP servers used in FactMarrow are either:**
- Open-source and self-hosted
- Free tier from major providers
- Already in your subscriptions

**No new subscriptions required.**
