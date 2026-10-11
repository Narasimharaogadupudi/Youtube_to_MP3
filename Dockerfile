
FROM brainicism/bgutil-ytdlp-pot-provider:2.0.0-deno AS pot-provider

FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=pot-provider /usr/bin/deno /usr/bin/deno
COPY --from=pot-provider /app /opt/bgutil

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p downloads

CMD ["sh", "-c", "deno run --allow-env --allow-net --allow-ffi=/opt/bgutil/node_modules --allow-read=/opt/bgutil/node_modules /opt/bgutil/src/main.ts --host 127.0.0.1 --port 4416 & exec gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 300 app:app"]
