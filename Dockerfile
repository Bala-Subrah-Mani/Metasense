# MetaSense container: a clean, OS-independent way to run the CLI and the test suite.
# Build:  docker build -t metasense:0.2.3 .
# Run:    docker run --rm -v "$PWD/data/sample:/data:ro" metasense:0.2.3 analyze /data/paper_weak.txt
# Tests:  docker run --rm --entrypoint python metasense:0.2.3 -m pytest -q
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY requirements.txt requirements-dev.txt pyproject.toml README.md ./
COPY src ./src
RUN pip install -r requirements-dev.txt && pip install .

# Tests, sample data and configuration are copied so the container can verify itself.
COPY tests ./tests
COPY data ./data
COPY config ./config
COPY scripts ./scripts

RUN useradd --create-home metasense && chown -R metasense /app
USER metasense
ENTRYPOINT ["metasense"]
CMD ["--help"]
