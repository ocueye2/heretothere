FROM  python:3.12.3-slim
WORKDIR /app


RUN pip install cherrypy pillow qrcode
RUN apt-get update
RUN apt-get install nano

# clone repo
RUN apt-get install git
RUN git clone https://github.com/ocueye2/my-website.git
RUN pip install cherrypy


EXPOSE 8170


WORKDIR /app/heretothere
CMD ["python", "start.py"]
