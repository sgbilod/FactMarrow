# FactMarrow: Scientific Analysis of Public Health Documents

Find the truth in health claims. FactMarrow is an open-source, multi-agent AI system that analyzes public health documents for scientific soundness, extracts claims, verifies facts against authoritative sources, and generates evidence-based reports.

## Mission

**Find the Truth of Everything**

FactMarrow helps separate evidence-based claims from speculation in public health documents through rigorous, multi-source fact-checking powered by AI.

## Features

✅ **Multi-Agent Analysis** - Specialized agents for parsing, extraction, verification, reporting
✅ **Real-Time Fact Verification** - Cross-references 50+ authoritative sources (CDC, WHO, PubMed, FDA, Data Commons)
✅ **Evidence-Based Confidence Ratings** - Transparent about certainty levels
✅ **Semantic Search** - Find similar analyses and claims
✅ **CI/CD Integration** - Analyze documents via GitHub Issues or API
✅ **Open Source & Free** - Built entirely on free/open-source tools
✅ **Zero Cost Infrastructure** - Uses your existing subscriptions (Claude Pro, GitHub Pro+, Docker Pro+)

## Architecture

### Six-Agent Coordinated System

FactMarrow uses Docker's Cagent runtime with specialized agents:

1. **Root Coordinator** - Orchestrates workflow and delegates tasks
2. **Document Processor** - Parses documents and extracts metadata
3. **Fact Extractor** - Identifies quantitative and causal claims
4. **Verification Specialist** - Cross-references with authoritative sources
5. **Report Writer** - Generates comprehensive analysis reports
6. **Quality Reviewer** - Performs final QA and fact-checking

### Data Flow

```
Document Upload
     ↓
Document Processor (parsing)
     ↓
Fact Extractor (claim identification)
     ↓
Verification Specialist (fact-checking)
     ↓
Report Writer (synthesis)
     ↓
Quality Reviewer (QA)
     ↓
Analysis Report (GitHub Issue / Database)
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Cagent (Docker's AI agent runtime)
- Claude Pro account
- GitHub Pro+ account

### Installation

```bash
# Clone the repository
git clone https://github.com/sgbilod/FactMarrow.git
cd FactMarrow

# Install dependencies
make install

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start services
make setup
```

### First Analysis

```bash
# Run analysis on a document
make run < your_document.txt

# Or via GitHub: Create an issue with label 'document-analysis'
```

## MCP Servers Integrated

FactMarrow leverages these Model Context Protocol servers:

| Server | Purpose | Status |
|--------|---------|--------|
| GitHub | Repository management | ✅ Configured |
| DuckDuckGo | Privacy web search | ✅ Configured |
| Filesystem | Local file operations | ✅ Configured |
| Data Commons | Public health datasets | ✅ Ready (NEW Oct 2025) |
| Chroma | Vector semantic search | ✅ Configured |
| PostgreSQL | Structured data storage | ✅ Configured |
| PubMed API | Peer-reviewed research | ✅ Available |
| FDA API | Drug/device data | ✅ Available |

## Usage

### Command Line

```bash
# Analyze a document
cagent run agents/factmarrow_agents.yaml < document.txt

# With configuration
cagent run agents/factmarrow_agents.yaml --config config/analysis_config.yaml
```

### GitHub Issues

Create an issue with label `document-analysis` and attach your document:

```markdown
## Document Analysis Request
- Document: [attached file]
- Focus areas: [specific claims to verify]
- Analysis depth: quick | standard | comprehensive
```

### API

```bash
curl -X POST http://localhost:8080/api/analyze \
  -F "document=@health_report.pdf" \
  -F "analysis_type=comprehensive"
```

## Results

Analysis results include:

- **Parsed Document Structure** - Sections, tables, metadata
- **Extracted Claims** - All quantitative and causal claims
- **Verification Status** - Strong/Moderate/Weak/Contradicted
- **Evidence Summary** - Supporting and contradicting sources
- **Methodological Assessment** - Study design and quality
- **Confidence Ratings** - Transparent uncertainty communication
- **Source Attribution** - All claims cited with URLs

## Cost Analysis

**FactMarrow Infrastructure:**
- Compute: $0 (your local machine)
- Cloud: $0 (Docker containers locally)
- AI Models: Leverages Claude Pro you already have
- Data Sources: All free tier or public APIs
- **Total Monthly Cost: $0**

Comparable commercial system: $20,000-50,000/month

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- MCP server integrations
- Agent prompt optimization
- New verification data sources
- UI/Dashboard development
- Documentation
- Test coverage

## Documentation

- [Complete Documentation](docs/)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Cagent Guide](docs/CAGENT_GUIDE.md)
- [MCP Servers](docs/MCP_SERVERS.md)
- [Resource Assessment](RESOURCE_ASSESSMENT.md)
- [Week 1 Execution Plan](WEEK1_EXECUTION.md)

## API Keys Required

All free tier available:

- [Anthropic Claude](https://console.anthropic.com) - Claude Pro
- [GitHub](https://github.com) - Pro+ account
- [Google Data Commons](https://datacommons.org) - Free
- [PubMed API](https://www.ncbi.nlm.nih.gov/home/develop/api/) - Free
- [FDA API](https://open.fda.gov) - Free

## License

MIT License - See LICENSE file

## Citation

If you use FactMarrow in your research:

```bibtex
@software{factmarrow2025,
  title={FactMarrow: Multi-Agent Analysis of Public Health Documents},
  author={FactMarrow Contributors},
  year={2025},
  url={https://github.com/sgbilod/FactMarrow}
}
```

## Support

- 📧 GitHub Issues for bugs and feature requests
- 💬 GitHub Discussions for questions
- 📖 Documentation in /docs

---

**Mission**: Find the Truth of Everything

FactMarrow separates evidence-based claims from speculation. Join us in building better health analysis.
