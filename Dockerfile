FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Seed DB and train model on build
RUN python data/seed_data.py && python ml/predictor.py

EXPOSE 8000 8501

# Default: run API (override with docker run ... streamlit run dashboard/app.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
