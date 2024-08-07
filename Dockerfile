FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY /app/ .

CMD ["fastapi", "run", "main.py", "--port", "80"]