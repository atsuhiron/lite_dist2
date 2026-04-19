Remove-Item -Recurse -Force dist/
uv build
uv publish --token $env:PYPI_TOKEN