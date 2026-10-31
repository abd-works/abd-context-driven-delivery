#!/bin/bash
# Cloud environment setup: build the venv and install CDD into .claude/ and .mcp.json.
# Set the environment's Setup script to: bash <repo>/scripts/cloud-setup.sh
set -e
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/pip install -q -e .
.venv/bin/python scripts/install.py --ide Claude
