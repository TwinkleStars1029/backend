FROM python:3.10
LABEL "language"="python"
LABEL "framework"="fastapi"
WORKDIR /src
COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
