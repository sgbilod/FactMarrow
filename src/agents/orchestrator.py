"""
FactMarrow Agent Orchestration Layer

This module coordinates the 6-agent system using the Cagent framework.
It manages agent lifecycle, tool bindings, workflow execution, and state management.

Agents:
  1. Root Coordinator - Orchestrates the analysis workflow
  2. Document Processor - Parses and extracts document metadata
  3. Fact Extractor - Identifies and extracts claims
  4. Verification Specialist - Verifies claims against sources
  5. Report Writer - Compiles analysis findings
  6. Quality Reviewer - Performs final quality assurance
"""

import asyncio
import json
import logging
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ═══════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════


class AnalysisStatus(str, Enum):
    """Analysis workflow status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    DOCUMENT_PARSING = "document_parsing"
    CLAIM_EXTRACTION = "claim_extraction"
    VERIFICATION = "verification"
    REPORT_GENERATION = "report_generation"
    QUALITY_REVIEW = "quality_review"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRole(str, Enum):
    """Agent roles in the workflow"""
    ROOT_COORDINATOR = "root"
    DOCUMENT_PROCESSOR = "document_processor"
    FACT_EXTRACTOR = "fact_extractor"
    VERIFICATION_SPECIALIST = "verification_specialist"
    REPORT_WRITER = "report_writer"
    QUALITY_REVIEWER = "quality_reviewer"


@dataclass
class DocumentMetadata:
    """Extracted document metadata"""
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    publication_date: Optional[str] = None
    institution: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[List[str]] = None


@dataclass
class ExtractedClaim:
    """A claim extracted from the document"""
    text: str
    type: str  # quantitative, qualitative, causal, etc.
    location: Optional[str] = None  # section reference
    confidence: float = 0.5  # initial confidence 0-1
    supporting_text: Optional[str] = None


@dataclass
class VerificationResult:
    """Result of claim verification"""
    claim_text: str
    verification_status: str  # supported, contradicted, uncertain, unverifiable
    confidence: float  # 0-100
    supporting_sources: List[str] = field(default_factory=list)
    contradicting_sources: List[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class AnalysisState:
    """Complete state of an analysis execution"""
    analysis_id: int
    document_id: int
    status: AnalysisStatus = AnalysisStatus.QUEUED
    document_metadata: Optional[DocumentMetadata] = None
    extracted_claims: List[ExtractedClaim] = field(default_factory=list)
    verifications: List[VerificationResult] = field(default_factory=list)
    report_content: Optional[str] = None
    qa_feedback: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    agent_logs: Dict[str, List[str]] = field(default_factory=dict)

    def add_log(self, agent: str, message: str):
        """Add message to agent's log"""
        if agent not in self.agent_logs:
            self.agent_logs[agent] = []
        self.agent_logs[agent].append(f"[{datetime.now().isoformat()}] {message}")

    def add_error(self, error: str):
        """Record an error"""
        self.errors.append(error)
        logger.error(f"Analysis {self.analysis_id}: {error}")


# ═══════════════════════════════════════════════════════════════════════════
# AGENT CONFIGURATION LOADER
# ═══════════════════════════════════════════════════════════════════════════


class AgentConfigLoader:
    """Loads and manages agent configurations from YAML"""

    def __init__(self, config_path: str):
        """Initialize configuration loader
        
        Args:
            config_path: Path to agents YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.agents: Dict[str, Dict[str, Any]] = {}
        self._load_config()

    def _load_config(self):
        """Load YAML configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.agents = self.config.get('agents', {})
        logger.info(f"Loaded {len(self.agents)} agent configurations")

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for specific agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent configuration dictionary
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent not found: {agent_name}")
        return self.agents[agent_name]

    def get_sub_agents(self, agent_name: str) -> List[str]:
        """Get sub-agents for given agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            List of sub-agent names
        """
        config = self.get_agent_config(agent_name)
        return config.get('sub_agents', [])

    def get_model(self, agent_name: str) -> str:
        """Get model specification for agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Model identifier
        """
        config = self.get_agent_config(agent_name)
        return config.get('model', 'anthropic/claude-sonnet-4-0')


# ═══════════════════════════════════════════════════════════════════════════
# MCP SERVER MANAGER
# ═══════════════════════════════════════════════════════════════════════════


class MCPServerManager:
    """Manages MCP server connections and tool bindings"""

    def __init__(self, config_path: str):
        """Initialize MCP server manager
        
        Args:
            config_path: Path to MCP servers configuration file
        """
        self.config_path = Path(config_path)
        self.servers: Dict[str, Any] = {}
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self._load_config()

    def _load_config(self):
        """Load MCP server configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        self.servers = config.get('mcp_servers', {})
        logger.info(f"Loaded {len(self.servers)} MCP server configurations")

    async def get_session(self, server_name: str) -> Optional[aiohttp.ClientSession]:
        """Get or create session for MCP server
        
        Args:
            server_name: Name of the server
            
        Returns:
            ClientSession or None if server not found
        """
        if server_name in self.sessions:
            return self.sessions[server_name]

        server_config = self.servers.get(server_name)
        if not server_config:
            logger.warning(f"Server not found: {server_name}")
            return None

        session = aiohttp.ClientSession()
        self.sessions[server_name] = session
        logger.debug(f"Created session for server: {server_name}")
        return session

    async def close_all(self):
        """Close all MCP server sessions"""
        for session in self.sessions.values():
            await session.close()
        self.sessions.clear()
        logger.info("Closed all MCP server sessions")

    def get_agent_tools(self, agent_role: str) -> List[str]:
        """Get available tools for an agent
        
        Args:
            agent_role: Role of the agent
            
        Returns:
            List of tool names
        """
        # This would typically read from MCP server config
        # For now, return role-appropriate tools
        tools_map = {
            'root': ['all'],
            'document_processor': ['read_file', 'list_directory'],
            'fact_extractor': ['read_file', 'search'],
            'verification_specialist': ['search', 'query_health_data'],
            'report_writer': ['write_file', 'create_issue'],
            'quality_reviewer': ['read_file', 'search'],
        }
        return tools_map.get(agent_role, [])


# ═══════════════════════════════════════════════════════════════════════════
# AGENT EXECUTOR
# ═══════════════════════════════════════════════════════════════════════════


class AgentExecutor:
    """Executes individual agent tasks within the workflow"""

    def __init__(self, agent_config: Dict[str, Any], mcp_manager: MCPServerManager):
        """Initialize agent executor
        
        Args:
            agent_config: Agent configuration dictionary
            mcp_manager: MCP server manager instance
        """
        self.agent_config = agent_config
        self.mcp_manager = mcp_manager
        self.model = agent_config.get('model', 'anthropic/claude-sonnet-4-0')
        self.instruction = agent_config.get('instruction', '')

    async def execute_task(
        self,
        task_prompt: str,
        context: Dict[str, Any],
        state: AnalysisState
    ) -> str:
        """Execute a task with the agent
        
        Args:
            task_prompt: The prompt/task for the agent
            context: Additional context data
            state: Current analysis state
            
        Returns:
            Agent response/output
        """
        logger.debug(f"Executing task with prompt length: {len(task_prompt)}")

        # For now, this is a placeholder that would use Claude API
        # In production, this would call the actual Anthropic API
        try:
            # Mock execution - replace with actual API call
            result = await self._mock_api_call(task_prompt, context)
            logger.debug(f"Task executed successfully, result length: {len(result)}")
            return result
        except Exception as e:
            state.add_error(f"Task execution failed: {str(e)}")
            raise

    async def _mock_api_call(self, prompt: str, context: Dict[str, Any]) -> str:
        """Mock API call (replace with real implementation)
        
        Args:
            prompt: The prompt
            context: Context data
            
        Returns:
            Mock response
        """
        # This is a placeholder - in production this would call Claude API
        await asyncio.sleep(0.1)  # Simulate API latency
        return json.dumps({
            "status": "success",
            "message": "Mock agent execution completed",
            "timestamp": datetime.now().isoformat()
        })


# ═══════════════════════════════════════════════════════════════════════════
# WORKFLOW ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════


class WorkflowOrchestrator:
    """Orchestrates the complete analysis workflow across all agents"""

    def __init__(
        self,
        agent_config_path: str,
        mcp_config_path: str
    ):
        """Initialize workflow orchestrator
        
        Args:
            agent_config_path: Path to agents configuration file
            mcp_config_path: Path to MCP servers configuration file
        """
        self.agent_loader = AgentConfigLoader(agent_config_path)
        self.mcp_manager = MCPServerManager(mcp_config_path)
        self.executors: Dict[str, AgentExecutor] = {}
        self.active_analyses: Dict[int, AnalysisState] = {}
        self._initialize_executors()

    def _initialize_executors(self):
        """Initialize agent executors for all configured agents"""
        for agent_name in self.agent_loader.agents.keys():
            try:
                config = self.agent_loader.get_agent_config(agent_name)
                executor = AgentExecutor(config, self.mcp_manager)
                self.executors[agent_name] = executor
                logger.info(f"Initialized executor for agent: {agent_name}")
            except Exception as e:
                logger.error(f"Failed to initialize executor for {agent_name}: {e}")

    async def execute_analysis(
        self,
        analysis_id: int,
        document_id: int,
        document_path: str,
        document_content: str
    ) -> AnalysisState:
        """Execute complete analysis workflow
        
        Args:
            analysis_id: ID of the analysis record
            document_id: ID of the document record
            document_path: Path to the document file
            document_content: Content of the document
            
        Returns:
            Final analysis state
        """
        state = AnalysisState(
            analysis_id=analysis_id,
            document_id=document_id,
            started_at=datetime.now()
        )

        self.active_analyses[analysis_id] = state

        try:
            logger.info(f"Starting analysis workflow for document_id={document_id}")
            state.add_log("orchestrator", "Analysis workflow started")

            # PHASE 1: Document Processing
            state.status = AnalysisStatus.DOCUMENT_PARSING
            await self._phase_document_processing(state, document_path, document_content)

            # PHASE 2: Fact Extraction
            state.status = AnalysisStatus.CLAIM_EXTRACTION
            await self._phase_fact_extraction(state)

            # PHASE 3: Verification
            state.status = AnalysisStatus.VERIFICATION
            await self._phase_verification(state)

            # PHASE 4: Report Generation
            state.status = AnalysisStatus.REPORT_GENERATION
            await self._phase_report_generation(state)

            # PHASE 5: Quality Review
            state.status = AnalysisStatus.QUALITY_REVIEW
            await self._phase_quality_review(state)

            state.status = AnalysisStatus.COMPLETED
            state.completed_at = datetime.now()
            state.add_log("orchestrator", "Analysis workflow completed successfully")
            logger.info(f"Analysis {analysis_id} completed successfully")

        except Exception as e:
            state.status = AnalysisStatus.FAILED
            state.completed_at = datetime.now()
            state.add_error(f"Workflow execution failed: {str(e)}")
            logger.error(f"Workflow execution failed for analysis {analysis_id}: {e}")

        return state

    async def _phase_document_processing(
        self,
        state: AnalysisState,
        document_path: str,
        document_content: str
    ) -> None:
        """Phase 1: Document Processing
        
        Args:
            state: Current analysis state
            document_path: Path to document
            document_content: Document content
        """
        logger.debug("Phase 1: Document Processing")
        state.add_log("document_processor", "Starting document processing")

        try:
            executor = self.executors.get('document_processor')
            if not executor:
                raise ValueError("Document processor executor not initialized")

            # Create task prompt
            prompt = f"""
            Parse and analyze the following document:
            
            Path: {document_path}
            Content length: {len(document_content)} characters
            
            Content preview (first 1000 chars):
            {document_content[:1000]}
            ...
            
            Extract:
            1. Document metadata (title, authors, date, institution)
            2. Document structure (sections, subsections)
            3. Tables and their contents
            4. References and citations
            
            Return JSON with: metadata, structure, tables, references, quality_issues
            """

            result = await executor.execute_task(prompt, {"path": document_path}, state)
            
            # Parse result
            parsed_result = json.loads(result) if isinstance(result, str) else result
            
            # Store metadata
            state.document_metadata = DocumentMetadata(
                title=parsed_result.get('metadata', {}).get('title'),
                authors=parsed_result.get('metadata', {}).get('authors', []),
                publication_date=parsed_result.get('metadata', {}).get('publication_date'),
                institution=parsed_result.get('metadata', {}).get('institution')
            )

            state.add_log(
                "document_processor",
                f"Extracted metadata: {state.document_metadata.title}"
            )

        except Exception as e:
            state.add_error(f"Document processing failed: {str(e)}")
            raise

    async def _phase_fact_extraction(self, state: AnalysisState) -> None:
        """Phase 2: Fact Extraction
        
        Args:
            state: Current analysis state
        """
        logger.debug("Phase 2: Fact Extraction")
        state.add_log("fact_extractor", "Starting fact extraction")

        try:
            executor = self.executors.get('fact_extractor')
            if not executor:
                raise ValueError("Fact extractor executor not initialized")

            # Create task prompt
            prompt = """
            Extract all claims from the document.
            For each claim, identify:
            1. Claim text
            2. Type (quantitative, qualitative, causal, etc.)
            3. Location/context (which section)
            4. Supporting evidence within the document
            
            Return JSON array with: text, type, location, supporting_text
            """

            result = await executor.execute_task(prompt, {"metadata": state.document_metadata}, state)
            
            # Parse claims (mock for now)
            parsed_result = json.loads(result) if isinstance(result, str) else result
            
            # Create ExtractedClaim objects
            claims_data = parsed_result.get('claims', [])
            for claim_data in claims_data:
                claim = ExtractedClaim(
                    text=claim_data.get('text', ''),
                    type=claim_data.get('type', 'unknown'),
                    location=claim_data.get('location'),
                    supporting_text=claim_data.get('supporting_text')
                )
                state.extracted_claims.append(claim)

            state.add_log("fact_extractor", f"Extracted {len(state.extracted_claims)} claims")

        except Exception as e:
            state.add_error(f"Fact extraction failed: {str(e)}")
            raise

    async def _phase_verification(self, state: AnalysisState) -> None:
        """Phase 3: Verification
        
        Args:
            state: Current analysis state
        """
        logger.debug("Phase 3: Verification")
        state.add_log("verification_specialist", "Starting claim verification")

        try:
            executor = self.executors.get('verification_specialist')
            if not executor:
                raise ValueError("Verification specialist executor not initialized")

            # Verify each claim
            for claim in state.extracted_claims:
                prompt = f"""
                Verify the following claim using authoritative sources:
                
                Claim: {claim.text}
                Type: {claim.type}
                
                Search for:
                1. Supporting evidence
                2. Contradicting evidence
                3. Relevant studies or reports
                4. Expert consensus
                
                Return JSON with: verification_status, supporting_sources, contradicting_sources, confidence, notes
                """

                result = await executor.execute_task(prompt, {"claim": claim.text}, state)
                parsed_result = json.loads(result) if isinstance(result, str) else result

                verification = VerificationResult(
                    claim_text=claim.text,
                    verification_status=parsed_result.get('verification_status', 'uncertain'),
                    confidence=parsed_result.get('confidence', 0),
                    supporting_sources=parsed_result.get('supporting_sources', []),
                    contradicting_sources=parsed_result.get('contradicting_sources', []),
                    notes=parsed_result.get('notes')
                )
                state.verifications.append(verification)

            state.add_log(
                "verification_specialist",
                f"Verified {len(state.verifications)} claims"
            )

        except Exception as e:
            state.add_error(f"Verification failed: {str(e)}")
            raise

    async def _phase_report_generation(self, state: AnalysisState) -> None:
        """Phase 4: Report Generation
        
        Args:
            state: Current analysis state
        """
        logger.debug("Phase 4: Report Generation")
        state.add_log("report_writer", "Starting report generation")

        try:
            executor = self.executors.get('report_writer')
            if not executor:
                raise ValueError("Report writer executor not initialized")

            # Generate comprehensive report
            prompt = f"""
            Generate a comprehensive analysis report based on:
            
            Document: {state.document_metadata.title if state.document_metadata else "Unknown"}
            Claims analyzed: {len(state.extracted_claims)}
            Verifications completed: {len(state.verifications)}
            
            Report should include:
            1. Executive summary
            2. Document overview
            3. Claims analysis (extracted claims with verification results)
            4. Verification findings
            5. Key findings and recommendations
            6. Confidence scores
            
            Format as markdown with sections.
            """

            result = await executor.execute_task(prompt, {"state": asdict(state)}, state)
            state.report_content = result

            state.add_log("report_writer", "Report generation completed")

        except Exception as e:
            state.add_error(f"Report generation failed: {str(e)}")
            raise

    async def _phase_quality_review(self, state: AnalysisState) -> None:
        """Phase 5: Quality Review
        
        Args:
            state: Current analysis state
        """
        logger.debug("Phase 5: Quality Review")
        state.add_log("quality_reviewer", "Starting quality review")

        try:
            executor = self.executors.get('quality_reviewer')
            if not executor:
                raise ValueError("Quality reviewer executor not initialized")

            # Perform QA review
            prompt = f"""
            Review the quality and accuracy of the analysis report:
            
            Report preview:
            {state.report_content[:1000] if state.report_content else "No report"}
            
            Check for:
            1. Logical consistency
            2. Evidence quality
            3. Confidence score appropriateness
            4. Citation completeness
            5. Overall report quality
            
            Provide feedback and confidence score (0-100).
            Return JSON with: feedback, confidence, approved_for_publication
            """

            result = await executor.execute_task(prompt, {"report": state.report_content}, state)
            parsed_result = json.loads(result) if isinstance(result, str) else result

            state.qa_feedback = parsed_result.get('feedback')

            state.add_log(
                "quality_reviewer",
                f"Quality review completed, confidence: {parsed_result.get('confidence')}"
            )

        except Exception as e:
            state.add_error(f"Quality review failed: {str(e)}")
            raise

    def get_analysis_state(self, analysis_id: int) -> Optional[AnalysisState]:
        """Get current state of an analysis
        
        Args:
            analysis_id: ID of the analysis
            
        Returns:
            Analysis state or None if not found
        """
        return self.active_analyses.get(analysis_id)

    async def close(self):
        """Clean up resources"""
        await self.mcp_manager.close_all()
        logger.info("Orchestrator closed")


# ═══════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR FACTORY
# ═══════════════════════════════════════════════════════════════════════════


class OrchestratorFactory:
    """Factory for creating workflow orchestrator instances"""

    _instance: Optional[WorkflowOrchestrator] = None

    @classmethod
    def get_orchestrator(cls) -> WorkflowOrchestrator:
        """Get or create orchestrator singleton
        
        Returns:
            WorkflowOrchestrator instance
        """
        if cls._instance is None:
            # Get config paths from environment or use defaults
            project_root = Path(__file__).parent.parent.parent
            agent_config = os.getenv(
                'AGENT_CONFIG_PATH',
                str(project_root / 'agents' / 'factmarrow_agents.yaml')
            )
            mcp_config = os.getenv(
                'MCP_CONFIG_PATH',
                str(project_root / 'config' / 'mcp_servers.yaml')
            )

            cls._instance = WorkflowOrchestrator(agent_config, mcp_config)
            logger.info("Orchestrator singleton created")

        return cls._instance

    @classmethod
    def reset(cls):
        """Reset singleton (for testing)"""
        cls._instance = None


# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    """Demo execution of orchestrator"""
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def main():
        """Main demo"""
        try:
            logger.info("Initializing FactMarrow Agent Orchestrator")
            orchestrator = OrchestratorFactory.get_orchestrator()

            # Demo: Execute analysis
            demo_document = """
            # COVID-19 Transmission Study
            
            This study found that transmission rates increased by 50% in winter months.
            Sample size: 10,000 participants across 5 countries.
            
            Key findings:
            - Indoor transmission 3x higher than outdoor
            - Vaccination effectiveness: 85%
            - Breakthrough infections: 2%
            """

            logger.info("Executing demo analysis")
            state = await orchestrator.execute_analysis(
                analysis_id=1,
                document_id=1,
                document_path="demo_document.txt",
                document_content=demo_document
            )

            logger.info(f"Analysis completed with status: {state.status}")
            logger.info(f"Extracted {len(state.extracted_claims)} claims")
            logger.info(f"Verified {len(state.verifications)} claims")
            logger.info(f"Errors: {len(state.errors)}")

            # Print state summary
            print("\n" + "="*80)
            print("ANALYSIS STATE SUMMARY")
            print("="*80)
            print(f"Status: {state.status}")
            print(f"Claims: {len(state.extracted_claims)}")
            print(f"Verifications: {len(state.verifications)}")
            print(f"Errors: {len(state.errors)}")
            print("="*80 + "\n")

        except Exception as e:
            logger.error(f"Demo failed: {e}", exc_info=True)
            sys.exit(1)

    asyncio.run(main())
