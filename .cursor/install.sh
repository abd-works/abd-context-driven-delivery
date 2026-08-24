#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for abd-context-driven-delivery
# plus a sibling checkout of Paradise-Mobile/pml-domainmodel.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONIOENCODING=utf-8

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  python3 -m venv "$ROOT/.venv"
fi
"$ROOT/.venv/bin/python" -m pip install --upgrade pip
"$ROOT/.venv/bin/python" -m pip install -r "$ROOT/requirements.txt"
"$ROOT/.venv/bin/python" -m pip install -e "$ROOT"

PML_DEST="${PML_DOMAINMODEL_PATH:-/home/ubuntu/pml-domainmodel}"
PML_REPO="https://github.com/Paradise-Mobile/pml-domainmodel.git"

origin_url="$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)"
clone_url="$PML_REPO"
if [[ "$origin_url" == https://*@github.com/* ]]; then
  # Reuse this agent's GitHub token for the sibling org/repo (never echo it).
  clone_url="${origin_url%%@github.com*}@github.com/Paradise-Mobile/pml-domainmodel.git"
fi

if [[ -d "$PML_DEST/.git" ]]; then
  git -C "$PML_DEST" fetch --all --prune
  git -C "$PML_DEST" pull --ff-only || true
elif git ls-remote "$clone_url" HEAD >/dev/null 2>&1; then
  git clone "$clone_url" "$PML_DEST"
  echo "Cloned Paradise-Mobile/pml-domainmodel to $PML_DEST"
else
  echo "WARN: GitHub token cannot reach Paradise-Mobile/pml-domainmodel." >&2
  echo "WARN: Grant the Cursor GitHub App access to that repo, then relaunch." >&2
  echo "WARN: Or create a multi-repo Cloud Agent environment that selects both:" >&2
  echo "WARN:   github.com/abd-works/abd-context-driven-delivery" >&2
  echo "WARN:   github.com/Paradise-Mobile/pml-domainmodel" >&2
fi
