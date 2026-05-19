# Issues Solved

This document tracks important technical issues encountered during development and how they were solved.

## 1. Git Author Identity Unknown

### Problem

Git commit failed with:

```text
Author identity unknown
Please tell me who you are.
Cause

The Ubuntu VM did not have Git user identity configured.

Solution

Configured Git globally:

git config --global user.email "daniel5810005@gmail.com"
git config --global user.name "daniel5812"
2. Git Push Rejected — Remote Had Changes
Problem

Push failed with:

rejected main -> main (fetch first)
Cause

The GitHub repository had commits that were not present locally, likely from initial README creation on GitHub.

Solution

Used rebase:

git pull --rebase origin main

Resolved README conflict and pushed again.

3. HTTPS GitHub Authentication Failed
Problem

Push failed from VS Code Remote SSH:

Missing or invalid credentials
No anonymous write access
Authentication failed
Cause

The repository used HTTPS remote, but the Ubuntu VM did not have valid GitHub credentials.

Solution

Switched Git remote to SSH.

Steps:

cat ~/.ssh/id_ed25519.pub

Added the public key to GitHub:

GitHub → Settings → SSH and GPG keys → New SSH key

Then changed remote:

git remote set-url origin git@github.com:daniel5812/private-rag-platform.git
4. Docker Command Permission Denied
Problem

Docker worked with sudo, but failed without it:

permission denied while trying to connect to the docker API
Cause

The user was not active in the docker group in the current shell session.

Solution

Added user to Docker group:

sudo usermod -aG docker daniel

Then restarted the SSH/VS Code Remote session.

In some cases, VS Code Remote Server had to be restarted or the VM rebooted.

5. Docker Image Pull Failed — No Space Left on Device
Problem

Pulling the Ollama image failed:

no space left on device
Cause

The Ubuntu root filesystem was initially too small for Docker + Ollama + models.

Solution

Expanded the VMware virtual disk to 50GB.

Then expanded Ubuntu partition and LVM:

sudo growpart /dev/sda 3
sudo pvresize /dev/sda3
sudo lvextend --resizefs -l +100%FREE /dev/ubuntu-vg/ubuntu-lv

Verified with:

df -h
lsblk
6. FastAPI ResponseValidationError for UUID
Problem

Document upload inserted the document into the database, but the API returned a 500 error.

Log showed:

ResponseValidationError:
Input should be a valid string
input: UUID(...)
Cause

The Pydantic response model expected id as a string, but asyncpg returned it as a Python UUID object.

Solution

Converted the ID before returning:

document = dict(row)
document["id"] = str(document["id"])
return document
7. Retrieval Returned Empty Results
Problem

POST /rag/retrieve returned:

{
  "results": []
}
Cause

The document_chunks table was empty. The database volume had likely been reset during development.

Solution

Uploaded a new test document and confirmed chunks existed:

SELECT tenant_id, COUNT(*) total, COUNT(embedding) with_embedding
FROM document_chunks
GROUP BY tenant_id;

After uploading a new document, retrieval worked.

8. Wrong curl Formatting
Problem

Some curl commands failed with malformed URL or missing body.

Cause

There was a space after the line-continuation character:

curl ... \ 

In Bash, \ must be the final character on the line.

Solution

Use either a correct multiline command:

curl -i -X POST "http://localhost:8000/rag/retrieve" \
  -H "Content-Type: application/json" \
  -d '{"query":"access control","tenant_id":"demo","top_k":3}'

Or a single-line command.

9. Out of Memory Errors
Problem

The VM killed processes such as node and ollama:

Out of memory: Killed process
Cause

The VM had only 4GB RAM, which was not enough for VS Code Remote, Docker, PostgreSQL, Ollama, embeddings, and LLM generation.

Solution

Recommended increasing VM RAM to at least 8GB.

Recommended development resources:

Disk: 50GB
RAM: 8GB minimum
CPU: 2–4 cores
10. LLM Hallucinated Despite RAG Context
Problem

The answer generation endpoint worked, but the model added unsupported claims such as:

view, edit, or delete documents
compliance
authorized personnel
regulatory requirements

These did not appear in the retrieved context.

Cause

The local LLM tried to answer from general knowledge instead of staying strictly grounded in retrieved context.

Solution

Improved the prompt and added basic answer validation.

Implemented:

citation validation
allowed source ID checking
suspicious phrase detection
grounded fallback answer generation

This changed the answer from an unsupported definition to a safer grounded answer:

The document mentions access control in relation to internal company policy, permissions, secure document retrieval, and employee access management. [D1]