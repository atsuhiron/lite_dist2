FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml pyproject.toml
COPY README.md README.md

# Copy application code
COPY src/ src/
COPY docker_example/ example/

RUN pip install --upgrade pip && pip install --root-user-action=ignore --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "example.run_table"]
