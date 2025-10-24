# Phase 2 Implementation Plan - Agent Integration

**Date:** October 24, 2025
**Status:** 🟡 IN PROGRESS - Ready for Implementation
**Next Step:** Implement Agent Orchestration Layer

---

## Current State

### Completed
- [x] Test document submitted to /api/analyze
- [x] API responded with HTTP 200 OK
- [x] Document file accepted by FastAPI
- [x] All infrastructure services running
- [x] Agent configuration verified (6 agents)
- [x] MCP servers configured (8 services)
- [x] Database schema ready

### In Progress
- [ ] Implement document persistence to PostgreSQL
- [ ] Initialize Cagent framework and MCP connections
- [ ] Implement Root Coordinator agent orchestration
- [ ] Trigger document processing pipeline
- [ ] Execute 6-agent analysis workflow

### Current Issue

The `/api/analyze` endpoint is a placeholder:
- ✅ Receives file uploads
- ✅ Returns "Analysis queued"
- ❌ Does NOT save document to database
- ❌ Does NOT trigger agent workflow
- ❌ Does NOT process claims or verification

---

## Implementation Steps

### Step 1: Update API Endpoint

**File:** src/api/endpoints.py
**Function:** analyze_document()

Updates needed:
1. Save file to storage
2. Create document record in PostgreSQL
3. Trigger root coordinator agent
4. Return analysis ID to client

### Step 2: Initialize Cagent Framework

**File:** Create src/agents/orchestrator.py

Purpose:
1. Initialize Cagent framework
2. Load MCP server configurations
3. Create agent instances from YAML
4. Implement workflow coordination

### Step 3: Implement 6-Agent Workflow

Activate pipeline:
1. Root Coordinator → orchestrates workflow
2. Document Processor → parses structure
3. Fact Extractor → extracts claims
4. Verification Specialist → queries sources
5. Report Writer → generates report
6. Quality Reviewer → performs QA

---

## Database Operations

### Document Storage
```sql
INSERT INTO documents (title, file_path, content_hash)
VALUES ('test_covid_claim.txt', 'data/documents/test_covid_claim.txt', 'hash...');
```

### Claims Extraction
```sql
INSERT INTO claims (document_id, claim_text, claim_type, confidence)
VALUES (1, 'COVID vaccines prevented...', 'efficacy', 0.92);
```

### Verification Results
```sql
INSERT INTO verifications (claim_id, is_verified, confidence, sources)
VALUES (1, true, 0.95, '["Lancet", "WHO"]');
```

### Report Generation
```sql
INSERT INTO reports (document_id, analysis_summary, overall_confidence)
VALUES (1, 'Analysis summary...', 0.92);
```

### Final Analysis
```sql
INSERT INTO analyses (document_id, status, overall_confidence, qa_passed)
VALUES (1, 'completed', 0.92, true);
```

---

## Expected Workflow Timeline

| Phase | Task | Estimated Time |
|-------|------|-----------------|
| Document Processing | Parse structure | 2-3 sec |
| Fact Extraction | Extract claims | 3-5 sec |
| Verification | Query sources | 10-15 sec |
| Report Generation | Compile analysis | 2-3 sec |
| Quality Review | QA and scoring | 2-3 sec |
| Vector Embeddings | Store in Chroma | 3-5 sec |
| **Total** | **End-to-end** | **~30-40 sec** |

---

## Success Criteria

After implementation:

1. **Database Verification**
   - documents table: ≥1 record
   - claims table: ≥4 records
   - verifications table: ≥4 records
   - reports table: 1 record
   - analyses table: 1 record

2. **Vector DB Verification**
   - ≥1 collection created in Chroma
   - Embeddings stored for all claims

3. **API Response**
   - Status: "Analysis complete"
   - Claims extracted: 4-5
   - Overall confidence: 85-95%

4. **Performance**
   - Total execution time: <60 seconds
   - API response: <30 seconds

---

## Debugging Strategies

### Issue: Agent Not Responding
- Check Anthropic API key in .env
- Verify agent configuration in YAML
- Check agent coordination logs

### Issue: Database Insert Fails
- Verify referential integrity
- Check foreign key constraints
- Validate SQL syntax

### Issue: Vector Embedding Fails
- Verify Chroma service running
- Check Chroma endpoint accessible
- Restart if needed

---

## Next Actions

### Immediate (15-30 min)
1. Implement document persistence in /api/analyze
2. Create orchestrator.py
3. Update endpoint to trigger root coordinator

### Short-term (1-2 hours)
4. Test document submission
5. Monitor agent execution
6. Verify database population

### Medium-term (2-4 hours)
7. Generate Phase 2 completion report
8. Document findings
9. Prepare Phase 3 (multi-document)

---

## Phase 2 Readiness Checklist

Infrastructure:
- [x] PostgreSQL running
- [x] Redis running
- [x] Chroma running
- [x] FastAPI running

Configuration:
- [x] Agents defined
- [x] MCP servers defined
- [x] API keys configured
- [x] Database ready

Implementation:
- [ ] API endpoint enhanced
- [ ] Orchestrator created
- [ ] Agent workflow activated
- [ ] Database operations working

Testing:
- [ ] End-to-end document analysis
- [ ] All tables populated
- [ ] Vector embeddings created
- [ ] Performance acceptable

---

**Current Status: 🟡 IN PROGRESS - API Integration Needed**

Ready to proceed with agent integration implementation.
