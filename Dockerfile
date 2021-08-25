FROM python:3.9-slim
LABEL maintainer="ryan@volkno.com"

RUN apt-get update -yq && apt-get upgrade -yq && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


ADD ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt --compile --no-cache-dir

COPY ./app /app
WORKDIR /app/
EXPOSE 8050
CMD ["python", "index.py"]

