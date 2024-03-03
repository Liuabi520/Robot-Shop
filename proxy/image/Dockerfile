FROM python:3

WORKDIR /app

RUN apt update && apt install -y \
    net-tools \
    iputils-ping \ 
    && rm -rf /var/lib/apt/lists/*

COPY server.py mock_client.py ./

EXPOSE 8080

CMD ["python", "server.py"]
