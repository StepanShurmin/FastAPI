FROM python:3.12
RUN mkdir /booking
WORKDIR /booking
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN chmod a+x /booking/docker/app.sh
RUN chmod a+x /booking/docker/celery.sh