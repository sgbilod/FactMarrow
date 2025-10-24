-- FactMarrow Database Schema

-- Documents Table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    authors TEXT,
    publication_date DATE,
    source_url TEXT,
    file_path VARCHAR(1000),
    content_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analyses Table
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    analysis_type VARCHAR(50),
    status VARCHAR(50),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Claims Table
CREATE TABLE claims (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analyses(id),
    claim_text TEXT NOT NULL,
    claim_type VARCHAR(50),
    confidence VARCHAR(50),
    location VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verifications Table
CREATE TABLE verifications (
    id SERIAL PRIMARY KEY,
    claim_id INTEGER REFERENCES claims(id),
    verification_status VARCHAR(50),
    supporting_sources TEXT,
    contradicting_sources TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports Table
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analyses(id),
    report_content TEXT,
    overall_quality VARCHAR(50),
    approved_for_publication BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_documents_created ON documents(created_at);
CREATE INDEX idx_analyses_document ON analyses(document_id);
CREATE INDEX idx_analyses_status ON analyses(status);
CREATE INDEX idx_claims_analysis ON claims(analysis_id);
CREATE INDEX idx_verifications_claim ON verifications(claim_id);
