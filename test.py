
from fastapi import FastAPI
import requests
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import json
from dotenv import load_dotenv

# Initialize environment variables
load_dotenv()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

# Define the API usage model
class APIUsage(Base):
    __tablename__ = 'api_usage'
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    # Use Text columns to accommodate larger JSON data
    request_data = Column(Text)
    response_data = Column(Text)

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

def log_usage(endpoint_name: str, request_data=None, response_data=None):
    # Serialize request and response data to JSON string
    serialized_request_data = json.dumps(request_data) if request_data else ''
    serialized_response_data = json.dumps(response_data) if response_data else ''
    # Create new APIUsage instance
    api_usage_log = APIUsage(endpoint=endpoint_name, request_data=serialized_request_data, response_data=serialized_response_data)
    db = SessionLocal()
    db.add(api_usage_log)
    db.commit()
    db.close()

@app.get("/api_usage")
async def get_api_usage():
    # Query the database for API usage data
    db = SessionLocal()
    data = db.query(APIUsage).all()
    db.close()
    # Return the data including request and response
    return [{
        "endpoint": usage.endpoint,
        "timestamp": usage.timestamp.isoformat(),
        "request_data": json.loads(usage.request_data) if usage.request_data else None,
        "response_data": json.loads(usage.response_data) if usage.response_data else None
    } for usage in data]

@app.post("/test")
async def llm_insight(user_prompt: str):
    # External API URL from environment variables
    url = os.getenv("API_URL")
    headers = {"Content-Type": "application/json"}
    request_data = {
        "useCase": "FINANCE_DATA_AGENT",
        "contextId": "PYTHON_AGENT",
        "preSeed_injection_map": {"{USER_PROMPT}": user_prompt},
        "parameters": {"temperature": 0.9, "maxOutputTokens": 2048, "topP": 1},
    }
    response = requests.post(url, json=request_data, headers=headers)
    if response.status_code == 200:
        # On success, log the request and response data
        response_data = response.json()
        log_usage("/test", request_data=request_data, response_data=response_data)
        return response_data["prediction"]
    else:
        # On failure, log the attempt with an empty response
        log_usage("/test", request_data=request_data, response_data={})
        return {"error": "External API call failed", "status_code": response.status_code}
