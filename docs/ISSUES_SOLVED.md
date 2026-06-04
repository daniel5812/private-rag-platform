# Issues Solved

This document tracks important technical issues encountered during development and how they were solved.

## 1. Git Author Identity Unknown

### Problem

Git commit failed with:

```
Author identity unknown
Please tell me who you are.
```

### Cause

The Ubuntu VM did not have Git user identity configured.

### Solution

Configured Git globally:

```bash
git config --global user.email "daniel5810005@gmail.com"
git config --global user.name "daniel5812"
```

## 2. Git Push Rejected — Remote Had Changes

### Problem

Push failed with:

```
rejected main -> main (fetch first)
```

### Cause

The GitHub repository had commits that were not present locally, likely from initial README creation on GitHub.

### Solution

Used rebase:

```bash
git pull --rebase origin main
```

Resolved README conflict and pushed again.

## 3. HTTPS GitHub Authentication Failed

### Problem

Push failed from VS Code Remote SSH:

```
Missing or invalid credentials
No anonymous write access
Authentication failed
```

### Cause

The repository used HTTPS remote, but the Ubuntu VM did not have valid GitHub credentials.

### Solution

Switched Git remote to SSH.

Steps:

```bash
cat ~/.ssh/id_ed25519.pub
```

Added the public key to GitHub:

GitHub → Settings → SSH and GPG keys → New SSH key

Then changed remote:

```bash
git remote set-url origin git@github.com:daniel5812/private-rag-platform.git
```

## 4. Docker Command Permission Denied

### Problem

Docker worked with sudo, but failed without it:

```
permission denied while trying to connect to the docker API
```

### Cause

The user was not active in the docker group in the current shell session.

### Solution

Added user to Docker group:

```bash
sudo usermod -aG docker daniel
```

Then restarted the SSH/VS Code Remote session. In some cases, VS Code Remote Server had to be restarted or the VM rebooted.

## 5. Docker Image Pull Failed — No Space Left on Device

### Problem

Pulling the Ollama image failed:

```
no space left on device
```

### Cause

The Ubuntu root filesystem was initially too small for Docker + Ollama + models.

### Solution

Expanded the VMware virtual disk to 50GB.

Then expanded Ubuntu partition and LVM:

```bash
sudo growpart /dev/sda 3
sudo pvresize /dev/sda3
sudo lvextend --resizefs -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
```

Verified with:

```bash
df -h
lsblk
```

## 6. FastAPI ResponseValidationError for UUID

### Problem

Document upload inserted the document into the database, but the API returned a 500 error.

Log showed:

```
ResponseValidationError:
Input should be a valid string
input: UUID(...)
```

### Cause

The Pydantic response model expected id as a string, but asyncpg returned it as a Python UUID object.

### Solution

Converted the ID before returning:

```python
document = dict(row)
document["id"] = str(document["id"])
return document
```

## 7. Retrieval Returned Empty Results

### Problem

`POST /rag/retrieve` returned:

```json
{
  "results": []
}
```

### Cause

The `document_chunks` table was empty. The database volume had likely been reset during development.

### Solution

Uploaded a new test document and confirmed chunks existed:

```sql
SELECT tenant_id, COUNT(*) total, COUNT(embedding) with_embedding
FROM document_chunks
GROUP BY tenant_id;
```

After uploading a new document, retrieval worked.

## 8. Wrong curl Formatting

### Problem

Some curl commands failed with malformed URL or missing body.

### Cause

There was a space after the line-continuation character:

```bash
curl ... \ 
```

In Bash, `\` must be the final character on the line.

### Solution

Use either a correct multiline command:

```bash
curl -i -X POST "http://localhost:8000/rag/retrieve" \
  -H "Content-Type: application/json" \
  -d '{"query":"access control","tenant_id":"demo","top_k":3}'
```

Or a single-line command.

## 9. Out of Memory Errors

### Problem

The VM killed processes such as node and ollama:

```
Out of memory: Killed process
```

### Cause

The VM had only 4GB RAM, which was not enough for VS Code Remote, Docker, PostgreSQL, Ollama, embeddings, and LLM generation.

### Solution

Recommended increasing VM RAM to at least 8GB.

Recommended development resources:

```
Disk: 50GB
RAM: 8GB minimum
CPU: 2–4 cores
```

## 10. LLM Hallucinated Despite RAG Context

### Problem

The answer generation endpoint worked, but the model added unsupported claims such as:

```
view, edit, or delete documents
compliance
authorized personnel
regulatory requirements
```

These did not appear in the retrieved context.

### Cause

The local LLM tried to answer from general knowledge instead of staying strictly grounded in retrieved context.

### Solution

Improved the prompt and added basic answer validation.

Implemented:

- Citation validation
- Allowed source ID checking
- Suspicious phrase detection
- Grounded fallback answer generation

This changed the answer from an unsupported definition to a safer grounded answer:

```
The document mentions access control in relation to internal company policy, 
permissions, secure document retrieval, and employee access management. [D1]
```

## 11. Empty PDF File Caused Cryptic Error

### Problem

Attempting to upload an empty PDF file caused a confusing traceback:

```
pypdf.errors.EmptyFileError
```

### Cause

The `pypdf` library raises an error when attempting to read an empty PDF, but the error was not caught or handled gracefully.

### Solution

Added explicit error handling in the PDF extraction logic:

```python
try:
    reader = PdfReader(pdf_file)
    if len(reader.pages) == 0:
        raise ValueError("The uploaded PDF file is empty")
except EmptyFileError:
    raise ValueError("The uploaded PDF file is empty")
```

Now returns HTTP 422 with:

```json
{"detail": "The uploaded PDF file is empty"}
```

## 12. Failed Document Uploads Left Orphaned Metadata

### Problem

If text extraction failed (e.g., unsupported PDF), the document metadata was already inserted into the database, but the chunks were never created. This left orphaned document records with zero chunks, confusing users and the API.

### Cause

The ingestion flow inserted metadata before extracting and storing chunks. If extraction failed midway, the document row existed but had no associated chunks.

### Solution

Reordered the ingestion flow:

1. Extract text from file
2. Split into chunks
3. Generate embeddings
4. Only then insert document metadata into the database

This ensures that either the full ingestion succeeds (metadata + chunks) or the entire operation fails cleanly.

## 13. pytest Could Not Find Tests in Docker

### Problem

Running `docker compose ... run api pytest tests -v` returned:

```
0 tests collected
```

Then when manually specifying tests:

```
ModuleNotFoundError: No module named 'app'
```

### Cause

1. The `Dockerfile` was not copying the `tests/` directory into the Docker image.
2. The Python path was not set, so imports of local modules (`from app import ...`) failed.

### Solution

Updated `backend/Dockerfile`:

```dockerfile
COPY tests/ /app/tests/

ENV PYTHONPATH=/app
```

Now pytest collects and runs all tests successfully.

## 14. Retrieval Threshold Too Permissive

### Problem

The retrieval endpoint returned results for every query, even when the most similar chunk was not actually relevant. For example, a query about "vacation policy" returned chunks about "access control" with distance 0.3779, which were not truly relevant.

### Cause

No distance threshold was applied. The system returned the top-k results regardless of similarity quality.

### Solution

Implemented distance-based filtering with a configurable threshold:

- Added `RETRIEVAL_MAX_DISTANCE` to environment configuration (default: 0.32)
- Added `filter_chunks_by_distance()` function to retrieval logic
- Chunks with distance > 0.32 are filtered out before returning results

The threshold was tuned empirically on the current dataset:

- access control query (distance 0.2608) → passes, returns relevant chunks
- vacation policy query (distance 0.3779) → filtered, returns empty (no relevant chunks)

**Note:** This is a heuristic threshold and should be evaluated on a proper test dataset with labeled relevance in future iterations. The threshold is configurable via environment variable for different deployments.

## 15. Workspace RAG Isolation

### Risk

The system supports multiple workspaces per tenant. Without explicit workspace filtering in retrieval, a query inside Workspace A could return chunks that belong to Workspace B — mixing unrelated document sets and producing incorrect, misleading answers.

### Root Cause

Early retrieval only filtered by `tenant_id`. When workspaces were introduced, retrieval needed to also filter by `workspace_id` to maintain isolation between workspaces within the same tenant.

### Solution

Three layers work together to enforce workspace isolation:

**1. Schema:** `workspace_id` is stored on both `documents` and `document_chunks`. Every chunk is associated with exactly one workspace at write time.

**2. Route validation:** Every workspace-scoped route calls `require_workspace(workspace_id, tenant_id)` before any data access. This confirms the workspace exists and belongs to the requesting tenant. Requests for a workspace that belongs to a different tenant are rejected before reaching retrieval.

**3. Retrieval SQL:** The `document_chunks` query in workspace-scoped RAG filters by both `tenant_id AND workspace_id`. Chunks from other workspaces are never returned, even if they are semantically similar.

**4. Tests:** Route tests verify that `workspace_id` is passed into the RAG service and that retrieval calls include the workspace filter. This prevents the isolation from being accidentally removed in a refactor.

### Clarification: Citation Validation Is Not a Security Boundary

`answer_uses_only_allowed_sources` checks that the LLM cites only source IDs that were included in the retrieved context. This is a hallucination guardrail — it prevents the model from fabricating or misattributing sources.

It does not enforce tenant or workspace access. By the time citation validation runs, retrieval has already been filtered by `tenant_id` and `workspace_id` at the SQL layer. The two mechanisms serve different purposes and should not be confused.

## 16. Development-only X-Tenant-ID Was Always Accepted

### Problem

`X-Tenant-ID` was added as a convenience for local development. Without any hardening, nothing prevented it from being used in non-development environments. Any client could set an arbitrary `X-Tenant-ID` and the backend would accept it as a valid tenant identity — there was no validation that the caller actually owned that tenant.

### Solution

Two changes were made together:

**1. JWT tenant resolution.** The backend now checks for `Authorization: Bearer <JWT>` on every request. If present, the token is validated against `JWT_SECRET_KEY` and `tenant_id` is extracted from the payload. JWT always wins over `X-Tenant-ID`. An invalid or expired token returns 401 and does not fall through to the header.

**2. `AUTH_DEV_MODE` flag.** `X-Tenant-ID` fallback is now gated behind a config field:

- `AUTH_DEV_MODE=true` — `X-Tenant-ID` / `demo` fallback allowed (local development)
- `AUTH_DEV_MODE=false` — requests without a valid JWT return 401; header fallback is not accepted

This means the development shortcut is explicit and opt-in, rather than always-on.

### Security Note

Real data isolation still depends on `require_workspace` and SQL filtering by `tenant_id + workspace_id`. JWT tenant resolution determines *who the caller is*; the workspace ownership check and retrieval filters determine *what data they can access*. Both layers are required.

### Tests

- `tests/test_tenant.py` — covers all JWT and AUTH_DEV_MODE scenarios
- `tests/test_workspace_rag_routes.py` — confirms workspace routes were not broken by the tenant resolution change
