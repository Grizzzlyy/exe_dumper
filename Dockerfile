FROM python:3.12
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "app.py"]
