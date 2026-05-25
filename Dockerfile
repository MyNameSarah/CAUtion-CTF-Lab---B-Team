FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y dnsutils && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m ctfuser
WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .

COPY flag.py /tmp/flag.py
RUN python3 /tmp/flag.py && rm /tmp/flag.py

USER ctfuser
EXPOSE 5000
CMD ["python", "app.py"]
