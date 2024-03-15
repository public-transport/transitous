FROM ghcr.io/motis-project/motis:latest

USER root
RUN mkdir -p /input/schedule && chown -R motis /input /system_config.ini
RUN apk add go python3 py3-pip

USER motis

RUN pip install requests
RUN go install github.com/patrickbr/gtfstidy@latest

# demo data for Aachen
RUN wget https://github.com/motis-project/test-data/raw/aachen/aachen.osm.pbf -O /input/osm.pbf

ADD --chown=motis src/ /tools/src
ADD --chown=motis feeds/ /tools/feeds
ADD --chown=motis transitland-atlas/ /tools/transitland-atlas
ADD config.ini /system_config.ini
ADD src/transitous /usr/local/bin/

RUN transitous fetch aachen.json
