#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
DEMO_TENANT="${DEMO_TENANT:-demo}"
ATTACKER_TENANT="${ATTACKER_TENANT:-attacker}"
QUERY_TEXT="${QUERY_TEXT:-What is the secret project code name?}"

echo "== Private RAG Platform: JWT RAG Flow Test =="
echo "API_BASE_URL=$API_BASE_URL"
echo "DEMO_TENANT=$DEMO_TENANT"
echo "ATTACKER_TENANT=$ATTACKER_TENANT"
echo ""

fail() {
  echo "[FAIL] $1"
  exit 1
}

ok() {
  echo "[OK] $1"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"
}

json_pretty() {
  python3 -m json.tool 2>/dev/null || cat
}

extract_json_field() {
  python3 -c "
import json, sys
data=json.load(sys.stdin)
field=sys.argv[1]
value=data
for part in field.split('.'):
    value=value[part]
print(value)
" "$1"
}

json_array_length() {
  python3 -c "
import json, sys
data=json.load(sys.stdin)
print(len(data))
"
}

assert_json_contains() {
  local expected="$1"

  python3 -c "
import json, sys
data = json.load(sys.stdin)
expected = sys.argv[1]
text = json.dumps(data)
if expected not in text:
    print(f'Expected text not found in JSON: {expected}', file=sys.stderr)
    sys.exit(1)
" "$expected"
}

assert_http_blocked() {
  local status_code="$1"
  local description="$2"

  case "$status_code" in
    401|403|404)
      ok "$description blocked with HTTP $status_code"
      ;;
    *)
      fail "$description was not blocked. Expected 401/403/404, got HTTP $status_code"
      ;;
  esac
}

create_workspace() {
  local name="$1"

  curl -fsS -X POST "$API_BASE_URL/workspaces" \
    -H "Authorization: Bearer $DEMO_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"$name\",
      \"description\": \"E2E JWT RAG flow test workspace\"
    }"
}

upload_test_document() {
  local workspace_id="$1"
  local test_file="/tmp/private-rag-e2e-test-document.txt"

  cat > "$test_file" <<'EOF'
Private RAG E2E Test Document

The secret project code name is Green Falcon.
The platform must use workspace-scoped retrieval.
The LLM is not the source of truth; documents and chunks are the source of truth.
EOF

  curl -fsS -X POST "$API_BASE_URL/workspaces/$workspace_id/documents/upload" \
    -H "Authorization: Bearer $DEMO_TOKEN" \
    -F "file=@$test_file;type=text/plain"
}

list_workspace_documents() {
  local workspace_id="$1"

  curl -fsS -X GET "$API_BASE_URL/workspaces/$workspace_id/documents" \
    -H "Authorization: Bearer $DEMO_TOKEN"
}

get_document_chunks() {
  local workspace_id="$1"
  local document_id="$2"

  curl -fsS -X GET "$API_BASE_URL/workspaces/$workspace_id/documents/$document_id/chunks" \
    -H "Authorization: Bearer $DEMO_TOKEN"
}

retrieve_from_workspace() {
  local workspace_id="$1"
  local query="$2"

  curl -fsS -X POST "$API_BASE_URL/workspaces/$workspace_id/rag/retrieve" \
    -H "Authorization: Bearer $DEMO_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"query\": \"$query\",
      \"top_k\": 3
    }"
}

ask_workspace() {
  local workspace_id="$1"
  local query="$2"

  curl -fsS -X POST "$API_BASE_URL/workspaces/$workspace_id/rag/ask" \
    -H "Authorization: Bearer $DEMO_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"query\": \"$query\",
      \"top_k\": 3
    }"
}

attacker_get_workspace_status() {
  local workspace_id="$1"

  curl -s -o /tmp/rag_attacker_workspace_response.json -w "%{http_code}" \
    -X GET "$API_BASE_URL/workspaces/$workspace_id" \
    -H "Authorization: Bearer $ATTACKER_TOKEN"
}

attacker_retrieve_status() {
  local workspace_id="$1"

  curl -s -o /tmp/rag_attacker_retrieve_response.json -w "%{http_code}" \
    -X POST "$API_BASE_URL/workspaces/$workspace_id/rag/retrieve" \
    -H "Authorization: Bearer $ATTACKER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"query\": \"$QUERY_TEXT\",
      \"top_k\": 3
    }"
}

require_cmd curl
require_cmd python3

if [ ! -x "./scripts/create-dev-token.py" ]; then
  fail "scripts/create-dev-token.py not found or not executable"
fi

if [ -z "${JWT_SECRET_KEY:-}" ]; then
  fail "JWT_SECRET_KEY is not set. Example: export JWT_SECRET_KEY='dev-secret'"
fi

export JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}"

echo "Creating JWT tokens..."
DEMO_TOKEN="$(./scripts/create-dev-token.py --tenant "$DEMO_TENANT")"
ATTACKER_TOKEN="$(./scripts/create-dev-token.py --tenant "$ATTACKER_TENANT")"

[ -n "$DEMO_TOKEN" ] || fail "Failed to create demo token"
[ -n "$ATTACKER_TOKEN" ] || fail "Failed to create attacker token"

ok "JWT created for tenant: $DEMO_TENANT"
ok "JWT created for tenant: $ATTACKER_TENANT"
echo ""

echo "Checking API health..."
curl -fsS "$API_BASE_URL/health" >/tmp/rag_health.json || fail "Health check failed"
ok "API health check passed"
cat /tmp/rag_health.json | json_pretty
echo ""

echo "Creating workspace..."
WORKSPACE_RESPONSE="$(create_workspace "JWT RAG Flow Test $(date +%s)")"
echo "$WORKSPACE_RESPONSE" | json_pretty

WORKSPACE_ID="$(echo "$WORKSPACE_RESPONSE" | extract_json_field "id")"
[ -n "$WORKSPACE_ID" ] || fail "Workspace ID was not returned"

WORKSPACE_TENANT_ID="$(echo "$WORKSPACE_RESPONSE" | extract_json_field "tenant_id")"
[ "$WORKSPACE_TENANT_ID" = "$DEMO_TENANT" ] || fail "Workspace tenant mismatch: expected $DEMO_TENANT, got $WORKSPACE_TENANT_ID"

ok "Workspace created: $WORKSPACE_ID"
echo ""

echo "Uploading test document..."
UPLOAD_RESPONSE="$(upload_test_document "$WORKSPACE_ID")"
echo "$UPLOAD_RESPONSE" | json_pretty

DOCUMENT_ID="$(echo "$UPLOAD_RESPONSE" | extract_json_field "id")"
[ -n "$DOCUMENT_ID" ] || fail "Document ID was not returned"

DOCUMENT_TENANT_ID="$(echo "$UPLOAD_RESPONSE" | extract_json_field "tenant_id")"
[ "$DOCUMENT_TENANT_ID" = "$DEMO_TENANT" ] || fail "Document tenant mismatch: expected $DEMO_TENANT, got $DOCUMENT_TENANT_ID"

DOCUMENT_WORKSPACE_ID="$(echo "$UPLOAD_RESPONSE" | extract_json_field "workspace_id")"
[ "$DOCUMENT_WORKSPACE_ID" = "$WORKSPACE_ID" ] || fail "Document workspace mismatch: expected $WORKSPACE_ID, got $DOCUMENT_WORKSPACE_ID"

ok "Document uploaded: $DOCUMENT_ID"
echo ""

echo "Listing workspace documents..."
DOCUMENTS_RESPONSE="$(list_workspace_documents "$WORKSPACE_ID")"
echo "$DOCUMENTS_RESPONSE" | json_pretty

DOCUMENTS_COUNT="$(echo "$DOCUMENTS_RESPONSE" | json_array_length)"
[ "$DOCUMENTS_COUNT" -ge 1 ] || fail "Expected at least one document in workspace"

ok "Workspace documents listed: $DOCUMENTS_COUNT document(s)"
echo ""

echo "Getting document chunks..."
CHUNKS_RESPONSE="$(get_document_chunks "$WORKSPACE_ID" "$DOCUMENT_ID")"
echo "$CHUNKS_RESPONSE" | json_pretty

CHUNKS_COUNT="$(echo "$CHUNKS_RESPONSE" | json_array_length)"
[ "$CHUNKS_COUNT" -ge 1 ] || fail "Expected at least one chunk for uploaded document"

ok "Document chunks returned: $CHUNKS_COUNT chunk(s)"
echo ""

echo "Running workspace retrieval..."
RETRIEVE_RESPONSE="$(retrieve_from_workspace "$WORKSPACE_ID" "$QUERY_TEXT")"
echo "$RETRIEVE_RESPONSE" | json_pretty

RETRIEVE_TENANT_ID="$(echo "$RETRIEVE_RESPONSE" | extract_json_field "tenant_id")"
[ "$RETRIEVE_TENANT_ID" = "$DEMO_TENANT" ] || fail "Retrieve tenant mismatch: expected $DEMO_TENANT, got $RETRIEVE_TENANT_ID"

ok "Workspace retrieval completed"
echo "$RETRIEVE_RESPONSE" | assert_json_contains "Green Falcon"
ok "Retrieval results contain expected test phrase"
echo ""


echo "Asking RAG question..."
ASK_RESPONSE="$(ask_workspace "$WORKSPACE_ID" "$QUERY_TEXT")"
echo "$ASK_RESPONSE" | json_pretty

ok "Workspace RAG ask completed"
echo "$ASK_RESPONSE" | assert_json_contains "Green Falcon"
ok "RAG ask sources contain expected test phrase"
echo ""

echo "Verifying tenant isolation..."
ATTACKER_WORKSPACE_STATUS="$(attacker_get_workspace_status "$WORKSPACE_ID")"
assert_http_blocked "$ATTACKER_WORKSPACE_STATUS" "Attacker workspace access"

ATTACKER_RETRIEVE_STATUS="$(attacker_retrieve_status "$WORKSPACE_ID")"
assert_http_blocked "$ATTACKER_RETRIEVE_STATUS" "Attacker workspace retrieval"
echo ""

ok "JWT RAG flow test completed successfully"