# set base image (host OS)
FROM python:3.11
# FROM python:3.10-slim-buster #In case of incompatibility with Raspberry Pi OS

# set the working directory in the container to /src
WORKDIR /src

# copy and install dependencies file to working directory
COPY requirements.txt .
# ENV MSGPACK_PUREPYTHON=1 #In case of incompatibility with Raspberry Pi OS
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copy the config file to working directory
COPY .env .

# copy the content of the local src directory to the working directory
COPY ./src /src

ENTRYPOINT ["python"]
CMD ["main.py"]
