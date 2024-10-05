FROM python:3.12
RUN mkdir /app
WORKDIR /app
COPY ./evil_twin /app
RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python3", "app.py"]
