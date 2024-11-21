FROM  python:3.12.3-slim
WORKDIR /app


RUN pip install cherrypy pillow qrcode
RUN apt-get update
RUN apt-get install nano

COPY . .

EXPOSE 8170

CMD ["python", "start.py"]
