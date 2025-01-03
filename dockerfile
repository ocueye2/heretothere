FROM  python:3.12.3-slim
WORKDIR /app


RUN pip install cherrypy pillow qrcode
RUN apt-get update
RUN apt-get install nano

# clone repo
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    git clone https://github.com/ocueye2/heretothere.git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install cherrypy

RUN git clone https://github.com/ocueye2/heretothere.git

EXPOSE 8170


WORKDIR /app/heretothere
CMD ["python", "start.py"]
