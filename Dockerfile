FROM python:3.12-slim-bullseye

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
# WORKDIR /app
# RUN rm -r data

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]