FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils && rm -rf /var/lib/apt/lists/*

# Fixed uid/gid so host-side permissions and compose overrides can rely on them.
RUN groupadd --system --gid 10001 opsagent \
    && useradd --system --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin opsagent

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

USER 10001:10001

EXPOSE 9100

CMD ["python", "agent.py"]
