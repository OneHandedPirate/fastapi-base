#!/bin/bash

PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$PROJECT_DIR/.venv/bin/activate"
export PYTHONPATH="$PROJECT_DIR"

gunicorn -c "$PROJECT_DIR/src/core/gunicorn_config.py" src.main:app