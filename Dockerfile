# Container image for running the experiments locally.
FROM python:3.11-slim

WORKDIR /work

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e .

COPY experiments ./experiments
COPY run_all.py ./

ENV RESULTS_DIR=/work/results \
    DATA_DIR=/work/data \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "run_all.py"]
