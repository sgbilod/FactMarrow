"""
Database Connection and Operations for FactMarrow

This module handles all database operations using asyncpg for high
performance.
"""

import logging
from typing import Optional, List, Dict
from datetime import datetime

import asyncpg

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages database connections and operations"""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize database connection"""
        self.db_host = "localhost"
        self.db_port = 5433
        self.db_user = "factmarrow"
        self.db_password = "michA3l0525#"
        self.db_name = "factmarrow"
        self.pool = None

    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                min_size=2,
                max_size=10,
            )
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def execute(self, query: str):
        """Execute raw SQL query"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query)

    # DOCUMENT OPERATIONS

    async def insert_document(
        self,
        title: str,
        file_path: str,
        content_hash: str,
        authors: Optional[str] = None,
        publication_date: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> int:
        """Insert document record"""
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO documents
                (title, authors, publication_date, source_url, file_path,
                 content_hash, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """
            result = await conn.fetchval(
                query,
                title,
                authors,
                publication_date,
                source_url,
                file_path,
                content_hash,
                datetime.now(),
                datetime.now()
            )
            return result

    async def get_document(self, document_id: int) -> Optional[Dict]:
        """Get document by ID"""
        async with self.pool.acquire() as conn:
            query = """
                SELECT id, title, authors, publication_date, source_url,
                       file_path, content_hash, created_at, updated_at
                FROM documents
                WHERE id = $1
            """
            row = await conn.fetchrow(query, document_id)
            return dict(row) if row else None

    # ANALYSIS OPERATIONS

    async def insert_analysis(
        self,
        document_id: int,
        analysis_type: str,
        status: str
    ) -> int:
        """Insert analysis record"""
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO analyses
                (document_id, analysis_type, status, started_at, created_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """
            result = await conn.fetchval(
                query,
                document_id,
                analysis_type,
                status,
                datetime.now(),
                datetime.now()
            )
            return result

    async def get_analysis(self, analysis_id: int) -> Optional[Dict]:
        """Get analysis by ID"""
        async with self.pool.acquire() as conn:
            query = """
                SELECT id, document_id, analysis_type, status,
                       started_at, completed_at, created_at
                FROM analyses
                WHERE id = $1
            """
            row = await conn.fetchrow(query, analysis_id)
            return dict(row) if row else None

    async def list_analyses(self) -> List[Dict]:
        """List all analyses"""
        async with self.pool.acquire() as conn:
            query = """
                SELECT id, document_id, analysis_type, status,
                       started_at, completed_at, created_at
                FROM analyses
                ORDER BY created_at DESC
                LIMIT 100
            """
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]

    async def update_analysis_status(
        self,
        analysis_id: int,
        status: str
    ):
        """Update analysis status"""
        async with self.pool.acquire() as conn:
            query = """
                UPDATE analyses
                SET status = $1,
                    completed_at = CASE WHEN $1 = 'completed'
                                    THEN $2
                                    ELSE completed_at
                                   END
                WHERE id = $3
            """
            await conn.execute(query, status, datetime.now(), analysis_id)

    # CLAIM OPERATIONS

    async def insert_claim(
        self,
        analysis_id: int,
        claim_text: str,
        claim_type: str,
        confidence: str,
        location: Optional[str] = None
    ) -> int:
        """Insert claim record"""
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO claims
                (analysis_id, claim_text, claim_type, confidence,
                 location, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """
            result = await conn.fetchval(
                query,
                analysis_id,
                claim_text,
                claim_type,
                confidence,
                location,
                datetime.now()
            )
            return result

    async def get_claims(self, analysis_id: int) -> List[Dict]:
        """Get claims for analysis"""
        async with self.pool.acquire() as conn:
            query = """
                SELECT c.id, c.analysis_id, c.claim_text, c.claim_type,
                       c.confidence, c.location, c.created_at,
                       v.verification_status
                FROM claims c
                LEFT JOIN verifications v ON c.id = v.claim_id
                WHERE c.analysis_id = $1
                ORDER BY c.created_at
            """
            rows = await conn.fetch(query, analysis_id)
            return [dict(row) for row in rows]

    async def get_claim_id_by_text(
        self,
        analysis_id: int,
        claim_text: str
    ) -> Optional[int]:
        """Get claim ID by text"""
        async with self.pool.acquire() as conn:
            query = """
                SELECT id FROM claims
                WHERE analysis_id = $1
                AND claim_text = $2
                LIMIT 1
            """
            result = await conn.fetchval(query, analysis_id, claim_text)
            return result

    # VERIFICATION OPERATIONS

    async def insert_verification(
        self,
        claim_id: int,
        verification_status: str,
        supporting_sources: Optional[str] = None,
        contradicting_sources: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:
        """Insert verification record"""
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO verifications
                (claim_id, verification_status, supporting_sources,
                 contradicting_sources, notes, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """
            result = await conn.fetchval(
                query,
                claim_id,
                verification_status,
                supporting_sources,
                contradicting_sources,
                notes,
                datetime.now()
            )
            return result

    # REPORT OPERATIONS

    async def insert_report(
        self,
        analysis_id: int,
        report_content: str,
        overall_quality: str = "draft",
        approved_for_publication: bool = False
    ) -> int:
        """Insert report record"""
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO reports
                (analysis_id, report_content, overall_quality,
                 approved_for_publication, created_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """
            result = await conn.fetchval(
                query,
                analysis_id,
                report_content,
                overall_quality,
                approved_for_publication,
                datetime.now()
            )
            return result

    async def get_report(self, analysis_id: int) -> Optional[Dict]:
        """Get report for analysis"""
        async with self.pool.acquire() as conn:
            query = """
                SELECT id, analysis_id, report_content, overall_quality,
                       approved_for_publication, created_at
                FROM reports
                WHERE analysis_id = $1
                ORDER BY created_at DESC
                LIMIT 1
            """
            row = await conn.fetchrow(query, analysis_id)
            return dict(row) if row else None
