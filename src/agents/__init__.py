"""
FactMarrow Agents Module

This package contains the multi-agent orchestration system for document analysis.

Agents:
  - Root Coordinator: Orchestrates the analysis workflow
  - Document Processor: Extracts document structure and metadata
  - Fact Extractor: Identifies and extracts claims
  - Verification Specialist: Verifies claims against sources
  - Report Writer: Compiles findings into reports
  - Quality Reviewer: Performs final quality assurance
"""

from .orchestrator import (
    OrchestratorFactory,
    WorkflowOrchestrator,
    AgentExecutor,
    AgentConfigLoader,
    MCPServerManager,
    AnalysisState,
    AnalysisStatus,
    AgentRole,
)

__all__ = [
    'OrchestratorFactory',
    'WorkflowOrchestrator',
    'AgentExecutor',
    'AgentConfigLoader',
    'MCPServerManager',
    'AnalysisState',
    'AnalysisStatus',
    'AgentRole',
]
