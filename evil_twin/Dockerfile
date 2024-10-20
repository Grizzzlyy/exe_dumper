FROM python:3.12
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
#RUN apt install libpq-dev python3-dev
EXPOSE 9090
ENTRYPOINT ["python3", "app.py"]
