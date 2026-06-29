FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY generate_marketing_data.py .
CMD ["python", "generate_marketing_data.py"]

