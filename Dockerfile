FROM python:3.12.15-slim-trixie

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Refresh distribution security fixes even when the published base image lags.
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip check \
    && python -m pip uninstall -y pip \
    && python -c "from pathlib import Path; import ensurepip; [p.unlink() for p in (Path(ensurepip.__file__).parent / '_bundled').glob('*.whl')]"

COPY . .

CMD ["python", "main.py"]
