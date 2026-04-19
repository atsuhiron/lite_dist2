#!/bin/bash
set -e

rm -rf dist/
uv build
uv publish --token "$PYPI_TOKEN"