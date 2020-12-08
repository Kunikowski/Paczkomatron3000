FROM python:3.8-slim
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install -r requirements.txt
ADD . /app
EXPOSE 8001
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8001", "app:app"]