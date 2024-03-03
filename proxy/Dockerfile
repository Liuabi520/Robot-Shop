FROM python:3

WORKDIR /app

RUN apt update && apt install -y net-tools

COPY server.py ./

EXPOSE 8080

CMD ["python", "server.py"]
