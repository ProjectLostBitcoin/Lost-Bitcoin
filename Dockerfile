# Lost Bitcoin — production image (zero-dependency Python stdlib app).
FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Deployed defaults: listen publicly on the platform port; keep the
# database and generated reports together on the mounted /data volume.
ENV HOST=0.0.0.0 \
    PORT=8080 \
    LOST_BITCOIN_DB=/data/lost_bitcoin.db \
    LOST_BITCOIN_REPORTS_DIR=/data/generated_reports

EXPOSE 8080

CMD ["python3", "app.py"]
