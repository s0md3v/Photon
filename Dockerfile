FROM python:3-slim-buster

LABEL name photon
LABEL src "https://github.com/s0md3v/Photon"
LABEL creator s0md3v
LABEL dockerfile_maintenance khast3x
LABEL desc "Incredibly fast crawler designed for reconnaissance."

RUN apt-get update && apt-get install -y git \
    && git clone https://github.com/s0md3v/Photon.git Photon
WORKDIR Photon
RUN pip install -r requirements.txt

VOLUME [ "/Photon" ]
# ENTRYPOINT ["sh"]
ENTRYPOINT [ "python", "photon.py" ]
CMD ["--help"]
