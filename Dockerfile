FROM python:3-alpine

LABEL name=photon
LABEL src="https://github.com/s0md3v/Photon"
LABEL desc="Incredibly fast crawler designed for OSINT."

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
VOLUME [ "/app/data" ]

ENTRYPOINT [ "python", "photon.py" ]
CMD ["--help"]
