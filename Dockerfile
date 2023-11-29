# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim

EXPOSE 8003

RUN apt update
RUN apt install gettext -y

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Create a volume
VOLUME /data/vet_client

COPY . /usr/src/app
WORKDIR /usr/src/app

# Install pip requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#CMD ["./vet/manage.py", "runserver", "0.0.0.0:8003"]  # as before

# run docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
