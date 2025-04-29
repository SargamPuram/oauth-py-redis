import os
import time
import redis
import requests
from dotenv import load_dotenv
from celery import Celery

load_dotenv()

# Setup Celery
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Load secrets
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")  # Set in .env
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Redis connection
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default"
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

@celery_app.task(name="main.store_token_task")
def store_token_task():
    token = get_token()
    r.set("oauth_token", token, ex=900)
    print("✅ Token stored in Redis for 15 minutes.")

def send_mock_request():
    token = r.get("oauth_token")
    if not token:
        print("❌ No token found in Redis. Exiting.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "CorrelationId": "test-corr-id",
        "ClientName": "my-client"
    }

    payload = {
        "serviceAccessDataDetails": {
            "clientName": "my-client",
            "globalTransactionId": "txn-001",
            "recordRestricted": False,
            "registerAccessed": True,
            "requestId": "req-001",
            "requestReason": "Verification",
            "requestTimestamp": "2025-04-23T12:00:00Z",
            "requesterType": "internal",
            "subjectRegisterId": "subject-12345"
        }
    }

    response = requests.post("http://localhost:5001/register/verified-identity/ARS12345", json=payload, headers=headers)
    print("✅ Mock request response:", response.json())

if __name__ == "__main__":
    # Trigger the Celery task and wait for it to complete
    print("🚀 Triggering token fetch task via Celery...")
    result = store_token_task.delay()

    try:
        result.get(timeout=10)  # Wait max 10 sec
        print("✅ Token fetch complete.")
    except Exception as e:
        print("❌ Token task failed or timed out:", str(e))
        exit()

    send_mock_request()
