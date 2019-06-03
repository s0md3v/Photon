FROM python:3-alpine

LABEL name photon
LABEL src "https://github.com/s0md3v/Photon"
LABEL creator s0md3v
LABEL dockerfile_maintenance khast3x
LABEL desc "Incredibly fast crawler designed for reconnaissance."

RUN apk add --no-cache git && git clone https://github.com/s0md3v/Photon.git Photon

RUN addgroup photon
RUN adduser -G photon -g "photon user" -s /bin/sh -D photon
RUN chown -R photon Photon
USER photon

WORKDIR Photon
RUN pip install --user -r requirements.txt

VOLUME [ "/Photon" ]
# ENTRYPOINT ["sh"]
ENTRYPOINT [ "python", "photon.py" ]
CMD ["--help"]
