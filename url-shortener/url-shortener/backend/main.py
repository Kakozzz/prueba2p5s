import os
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel

app = FastAPI(title="AWS URL Shortener API - UIDE", version="1.0.0")

# Configurar CORS para permitir peticiones desde S3
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "urls")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

class URLRequest(BaseModel):
    original_url: str

@app.post("/shorten", status_code=status.HTTP_201_CREATED)
def create_short_url(payload: URLRequest):
    short_code = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    item = {
        "short_code": short_code,
        "original_url": str(payload.original_url),
        "created_at": created_at
    }
    
    try:
        table.put_item(Item=item)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=e.response["Error"]["Message"])
    
    return {
        "short_code": short_code,
        "original_url": item["original_url"],
        "short_url": f"http://localhost:8000/{short_code}"
    }

@app.get("/{short_code}")
def redirect_to_original(short_code: str):
    try:
        response = table.get_item(Key={"short_code": short_code})
    except ClientError as e:
        raise HTTPException(status_code=500, detail=e.response["Error"]["Message"])
    
    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Short code not found")
    
    original_url = response["Item"]["original_url"]
    return RedirectResponse(url=original_url, status_code=307)

@app.get("/urls/{short_code}")
def get_url_info(short_code: str):
    try:
        response = table.get_item(Key={"short_code": short_code})
    except ClientError as e:
        raise HTTPException(status_code=500, detail=e.response["Error"]["Message"])
    
    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Short code not found")
        
    return response["Item"]