FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend .
RUN npm run build

FROM python:3.14-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev make && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend /app
COPY --from=frontend-build /frontend/dist /app/static
ENV DATABASE_URL=sqlite:///./people_pluse.db
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
