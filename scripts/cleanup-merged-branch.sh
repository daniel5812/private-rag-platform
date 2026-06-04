#!/usr/bin/env bash
set -e

BRANCH_TO_DELETE="$1"

if [ -z "$BRANCH_TO_DELETE" ]; then
  echo "Usage: ./scripts/cleanup-merged-branch.sh <branch-name>"
  exit 1
fi

git checkout main
git pull origin main

git grep "auth_dev_mode" >/dev/null || true

git branch -D "$BRANCH_TO_DELETE"

git push origin --delete "$BRANCH_TO_DELETE" || true

git status