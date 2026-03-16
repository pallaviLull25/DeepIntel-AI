#!/bin/sh
set -eu

exec python3 -m uvicorn backend.main:app "$@"
