FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHROMA_PERSIST_DIR=/tmp/campusit_chroma_db \
    PORT=7860
WORKDIR /code
RUN useradd -m -u 1000 appuser
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt
COPY --chown=appuser:appuser . /code
USER appuser
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
