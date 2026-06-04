#!/usr/bin/env bash
set -e

if [ ! -f "infra/docker-compose.yml" ]; then
  echo "Please run this script from the project root."
  exit 1
fi

CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" = "main" ]; then
  echo "You are on main. Create/use a feature branch first."
  exit 1
fi

echo "Current branch: $CURRENT_BRANCH"

echo "Checking git status..."
git status --short

if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree is not clean. Commit or stash your changes first."
  exit 1
fi

echo "Running tests..."
docker compose -f infra/docker-compose.yml run --rm api pytest tests/test_tenant.py -v
docker compose -f infra/docker-compose.yml run --rm api pytest tests/test_workspace_rag_routes.py -v

echo "Pushing branch..."
git push -u origin "$CURRENT_BRANCH"

echo "Creating PR..."
gh pr create \
  --fill \
  --base main \
  --head "$CURRENT_BRANCH"

echo ""
echo "PR created."
echo "Review it on GitHub, then run:"
echo ""
echo "gh pr merge --squash --delete-branch"
echo "git checkout main"
echo "git pull origin main"
echo "git branch -D $CURRENT_BRANCH"