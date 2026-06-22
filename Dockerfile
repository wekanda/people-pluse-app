FROM python:3.14-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev make && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . /app

# If you have prebuilt frontend assets, place them in backend/static
# The app will serve files from /app/static via FastAPI's StaticFiles

ENV DATABASE_URL=sqlite:///./people_pluse.db
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
