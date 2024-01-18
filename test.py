
from fastapi import FastAPI
import requests
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class APIUsage(Base):
    __tablename__ = 'api_usage'
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    request_data = Column(String)
    response_data = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()


def log_usage(endpoint_name: str, request_data=None, response_data=None):
    db = SessionLocal()
    api_usage_log = APIUsage(endpoint=endpoint_name, request_data=str(request_data), response_data=str(response_data))
    db.add(api_usage_log)
    db.commit()
    db.close()
    db = SessionLocal()
    api_usage_log = APIUsage(endpoint=endpoint_name)
    db.add(api_usage_log)
    db.commit()
    db.close()

@app.get("/hello_world_v1")
async def hello_world_v1():
    log_usage("hello_world_v1")
    return {"message": "Hello World v1"}

@app.get("/hello_world_v2")
async def hello_world_v2():
    log_usage("hello_world_v2")
    return {"message": "Hello World v2"}

@app.get("/api_usage")
async def get_api_usage():
    db = SessionLocal()
    data = db.query(APIUsage).all()
    db.close()
    return [{"endpoint": usage.endpoint, "timestamp": usage.timestamp.isoformat()} for usage in data]

@app.post("/api/prediction/LLMInsight")
async def llm_insight(useCase: str, contextId: str, preSeed_injection_map: dict, parameters: dict):
    # Assuming this endpoint calls an external API and returns the response
    external_api_url = 'https://external-api-url.com/predict'  # Replace with the actual external API URL
    request_data = {
        "useCase": useCase,
        "contextId": contextId,
        "preSeed_injection_map": preSeed_injection_map,
        "parameters": parameters
    }

    response = requests.post(external_api_url, json=request_data)
    if response.status_code == 200:
        # Log the usage
        log_data = {
            "request": request_data,
            "response": response.json() if response.status_code == 200 else {}
        }
        log_usage("api/prediction/LLMInsight", request_data=log_data["request"], response_data=log_data["response"])

        # Return the response from the external API
        return response.json()
    else:
        # If the API call failed, log the attempt with empty response data
        log_usage("api/prediction/LLMInsight", request_data=request_data, response_data={})
        return {"error": "External API call failed", "status_code": response.status_code}
