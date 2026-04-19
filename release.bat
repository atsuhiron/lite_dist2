rm -r dist/
uv build
uv publish --token "$PYPI_TOKEN"