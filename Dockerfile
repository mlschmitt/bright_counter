FROM python:3.13-alpine3.21

WORKDIR /app

COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

COPY . .

EXPOSE 9000

ENTRYPOINT ["python3"]
CMD ["app.py"]
