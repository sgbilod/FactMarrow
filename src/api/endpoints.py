"""FastAPI endpoints for FactMarrow

This module provides REST API endpoints for document submission and
analysis retrieval. It integrates with the agent orchestration system
to coordinate multi-agent document analysis.
"""

import os
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.agents import OrchestratorFactory, AnalysisStatus
from src.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════


class AnalysisResponse(BaseModel):
    """Response model for analysis submission"""
    analysis_id: int
    document_id: int
    status: str
    message: str
    timestamp: str


class AnalysisDetailResponse(BaseModel):
    """Response model for analysis details"""
    analysis_id: int
    document_id: int
    status: str
    document_title: Optional[str]
    claims_count: int
    verifications_count: int
    report_content: Optional[str]
    qa_feedback: Optional[str]
    errors: list
    created_at: Optional[str]
    completed_at: Optional[str]


# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="FactMarrow API",
    description="Multi-Agent Analysis of Public Health Documents",
    version="0.1.0-alpha"
)

# Initialize database connection
db = None
orchestrator = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global db, orchestrator
    try:
        db = DatabaseConnection()
        await db.initialize()
        logger.info("Database connection initialized")

        orchestrator = OrchestratorFactory.get_orchestrator()
        logger.info("Agent orchestrator initialized")
    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global orchestrator
    try:
        if orchestrator:
            await orchestrator.close()
            logger.info("Orchestrator closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}", exc_info=True)


# ═══════════════════════════════════════════════════════════════════════════
# HEALTH & STATUS
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "version": "0.1.0-alpha",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "database": "unknown",
            "orchestrator": "unknown"
        }
    }

    # Check database
    try:
        if db:
            await db.execute("SELECT 1")
            status["services"]["database"] = "running"
    except Exception as e:
        status["services"]["database"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check orchestrator
    try:
        if orchestrator:
            status["services"]["orchestrator"] = "running"
    except Exception as e:
        status["services"]["orchestrator"] = f"error: {str(e)}"
        status["status"] = "degraded"

    return status


# ═══════════════════════════════════════════════════════════════════════════
# DOCUMENT ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_document(file: UploadFile = File(...)):
    """Submit document for multi-agent analysis

    This endpoint:
    1. Saves the document file to disk
    2. Creates a database record
    3. Creates an analysis record
    4. Triggers the root coordinator agent
    5. Returns the analysis ID for status tracking

    Args:
        file: The document file to analyze (PDF, TXT, DOC)

    Returns:
        AnalysisResponse with analysis_id and status

    Raises:
        HTTPException: If analysis creation fails
    """
    try:
        logger.info(f"Analyzing document: {file.filename}")

        if not file.filename:
            raise ValueError("File must have a filename")

        if not orchestrator:
            raise RuntimeError("Orchestrator not initialized")

        # Read file content
        content = await file.read()
        if not content:
            raise ValueError("File is empty")

        # Create documents directory if needed
        docs_dir = Path("data/documents")
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Generate safe filename
        content_hash = hashlib.sha256(content).hexdigest()[:12]
        file_ext = Path(file.filename).suffix
        safe_filename = f"{content_hash}_{file.filename}"
        file_path = docs_dir / safe_filename

        # Save document to disk
        with open(file_path, 'wb') as f:
            f.write(content)
        logger.debug(f"Document saved to: {file_path}")

        # Create document record in database
        document_id = await db.insert_document(
            title=file.filename,
            file_path=str(file_path),
            content_hash=content_hash
        )
        logger.debug(f"Document record created: {document_id}")

        # Create analysis record in database
        analysis_id = await db.insert_analysis(
            document_id=document_id,
            analysis_type="full_assessment",
            status=AnalysisStatus.QUEUED.value
        )
        logger.debug(f"Analysis record created: {analysis_id}")

        # Convert bytes to string for processing
        document_content = content.decode('utf-8', errors='replace')

        # Trigger orchestrator workflow in background
        # In production, this would be queued to a task worker
        try:
            # Start analysis (this runs asynchronously in production)
            import asyncio

            async def run_analysis():
                try:
                    await db.update_analysis_status(
                        analysis_id,
                        AnalysisStatus.PROCESSING.value
                    )

                    state = await orchestrator.execute_analysis(
                        analysis_id=analysis_id,
                        document_id=document_id,
                        document_path=str(file_path),
                        document_content=document_content
                    )

                    # Update database with results
                    await db.update_analysis_status(
                        analysis_id,
                        state.status.value
                    )

                    # Store claims
                    for claim in state.extracted_claims:
                        await db.insert_claim(
                            analysis_id=analysis_id,
                            claim_text=claim.text,
                            claim_type=claim.type,
                            confidence=str(claim.confidence)
                        )

                    # Store verifications
                    for verification in state.verifications:
                        # Get claim ID
                        claim_id = await db.get_claim_id_by_text(
                            analysis_id,
                            verification.claim_text
                        )
                        if claim_id:
                            await db.insert_verification(
                                claim_id=claim_id,
                                verification_status=(
                                    verification.verification_status
                                ),
                                supporting_sources=(
                                    ",".join(
                                        verification.supporting_sources
                                    )
                                ),
                                contradicting_sources=(
                                    ",".join(
                                        verification.contradicting_sources
                                    )
                                ),
                                notes=verification.notes
                            )

                    # Store report
                    if state.report_content:
                        await db.insert_report(
                            analysis_id=analysis_id,
                            report_content=state.report_content,
                            overall_quality=(
                                "draft"
                                if state.status == AnalysisStatus.COMPLETED
                                else "pending_review"
                            )
                        )

                    logger.info(
                        f"Analysis {analysis_id} completed successfully"
                    )

                except Exception as e:
                    logger.error(
                        f"Background analysis failed for {analysis_id}: {e}",
                        exc_info=True
                    )
                    await db.update_analysis_status(
                        analysis_id,
                        AnalysisStatus.FAILED.value
                    )

            # Schedule background task
            asyncio.create_task(run_analysis())

        except Exception as e:
            logger.error(
                f"Failed to schedule analysis: {e}",
                exc_info=True
            )
            await db.update_analysis_status(
                analysis_id,
                AnalysisStatus.FAILED.value
            )

        return AnalysisResponse(
            analysis_id=analysis_id,
            document_id=document_id,
            status=AnalysisStatus.QUEUED.value,
            message=(
                f"Document queued for analysis. "
                f"Track progress with /api/analyses/{analysis_id}"
            ),
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Analysis submission failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis submission failed: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# ANALYSIS RETRIEVAL
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/api/analyses")
async def list_analyses():
    """List all analyses"""
    try:
        analyses = await db.list_analyses()
        return {
            "analyses": analyses,
            "total": len(analyses)
        }
    except Exception as e:
        logger.error(f"Failed to list analyses: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analyses"
        )


@app.get("/api/analyses/{analysis_id}",
         response_model=AnalysisDetailResponse)
async def get_analysis(analysis_id: int):
    """Get specific analysis details

    Args:
        analysis_id: ID of the analysis to retrieve

    Returns:
        Detailed analysis information including claims and verifications

    Raises:
        HTTPException: If analysis not found
    """
    try:
        # Get analysis
        analysis = await db.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found"
            )

        # Get document
        document = await db.get_document(analysis['document_id'])

        # Get claims
        claims = await db.get_claims(analysis_id)

        # Get report
        report = await db.get_report(analysis_id)

        # Get errors if available
        orchestrator_state = orchestrator.get_analysis_state(
            analysis_id
        )
        errors = (
            orchestrator_state.errors
            if orchestrator_state else []
        )

        return AnalysisDetailResponse(
            analysis_id=analysis_id,
            document_id=analysis['document_id'],
            status=analysis['status'],
            document_title=(
                document['title'] if document else None
            ),
            claims_count=len(claims),
            verifications_count=(
                sum(
                    1 for claim in claims
                    if claim.get('verification_status')
                )
            ),
            report_content=(
                report['report_content']
                if report else None
            ),
            qa_feedback=(
                report.get('approved_for_publication')
                if report else None
            ),
            errors=errors,
            created_at=analysis.get('created_at'),
            completed_at=analysis.get('completed_at')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to retrieve analysis {analysis_id}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analysis"
        )
