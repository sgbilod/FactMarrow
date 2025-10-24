# FactMarrow Architecture

## System Overview

FactMarrow is a multi-agent AI system built on Docker's Cagent runtime, orchestrating 6 specialized agents to analyze public health documents with scientific rigor.

## Core Components

### 1. Root Coordinator Agent
- **Role:** Orchestrates workflow and delegates tasks
- **Inputs:** Document + analysis request
- **Outputs:** Comprehensive analysis report
- **Responsibilities:**
  - Parse incoming requests
  - Delegate to specialized agents
  - Synthesize findings
  - Manage quality assurance

### 2. Document Processor Agent
- **Role:** Parses documents and extracts structure
- **Inputs:** Raw documents (PDF, text)
- **Outputs:** Structured document representation
- **Responsibilities:**
  - Extract metadata (title, authors, date)
  - Identify sections and hierarchy
  - Extract tables and citations
  - Clean and normalize text

### 3. Fact Extractor Agent
- **Role:** Identifies and categorizes claims
- **Inputs:** Structured document
- **Outputs:** Extracted claims with metadata
- **Claim Categories:**
  - Quantitative (statistics, percentages)
  - Causal (cause-effect relationships)
  - Methodological (study design)
  - Definitional (what is X)
  - Prescriptive (recommendations)

### 4. Verification Specialist Agent
- **Role:** Cross-references claims with authoritative sources
- **Inputs:** Extracted claims
- **Outputs:** Verification status with evidence
- **Data Sources:**
  - PubMed (peer-reviewed research)
  - CDC/WHO (government surveillance)
  - FDA (drug/device approvals)
  - Data Commons (public health data)
  - News sources

### 5. Report Writer Agent
- **Role:** Synthesizes findings into professional reports
- **Inputs:** Verification results
- **Outputs:** Markdown analysis report
- **Report Sections:**
  - Executive summary
  - Claim-by-claim analysis
  - Methodological assessment
  - Key findings
  - Source attribution

### 6. Quality Reviewer Agent
- **Role:** Performs final QA and fact-checking
- **Inputs:** Complete analysis report
- **Outputs:** Quality assessment + approval
- **Checks:**
  - Internal consistency
  - Source verification
  - Scientific rigor
  - Confidence appropriateness

## Data Flow

```
┌─────────────────────────────────────────────────────┐
│         Document Upload (GitHub/API/CLI)           │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │   Root Coordinator Agent     │
          │  (Task Delegation Hub)       │
          └──────────────────────────────┘
                    │  │  │  │  │
       ┌────────────┘  │  │  │  └─────────────┐
       │               │  │  │                │
       ▼               ▼  ▼  ▼                ▼
    ┌──────┐      ┌──────────┐         ┌──────────┐
    │ Doc  │      │ Fact     │         │Verif.    │
    │Proc. │      │Extract   │         │Specialist│
    └──┬───┘      └────┬─────┘         └────┬─────┘
       │               │                     │
       └───────────────┼─────────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
       ┌──────────┐          ┌──────────┐
       │ Report   │          │ Quality  │
       │ Writer   │◄─────────┤ Reviewer │
       └────┬─────┘          └──────────┘
            │
            ▼
    ┌──────────────────┐
    │ Final Report     │
    │ (GitHub + DB)    │
    └──────────────────┘
```

## Infrastructure

### Services
- **PostgreSQL:** Structured data storage
- **Redis:** Caching layer
- **Chroma:** Vector database for semantic search
- **Docker MCP Gateway:** Standardized tool access
- **API Server:** FastAPI application server

### MCP Servers Integrated
1. **GitHub MCP** - Repository management
2. **DuckDuckGo MCP** - Privacy web search
3. **Filesystem MCP** - Local file operations
4. **Data Commons MCP** - Public health datasets
5. **Custom MCP Servers** - Extensible architecture

## Scalability

### Horizontal Scaling
- Multiple analysis pipelines running in parallel
- Kubernetes deployment ready
- Load balancing via Docker Swarm or K8s

### Vertical Scaling
- Increased agent token limits
- Better models as available
- Additional MCP server integrations

## Security

### Per-Agent Permissions
- Document Processor: Read-only filesystem
- Verification: Web search + public APIs
- Report Writer: GitHub write access
- Quality Reviewer: Read-only verification

### Data Privacy
- Documents processed locally first
- External API calls only for verification
- GitHub repository control (public/private)
- No personal data transmitted

## Monitoring & Observability

- API request/response logging
- Agent decision tracking
- Analysis quality metrics
- Performance monitoring
- Error tracking via Sentry (optional)
