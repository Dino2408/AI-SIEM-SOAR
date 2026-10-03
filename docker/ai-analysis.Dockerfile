FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir "requests>=2.31"
COPY src/ai_analysis ./src/ai_analysis
RUN mkdir -p /data
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python","-m","src.ai_analysis.app"]
