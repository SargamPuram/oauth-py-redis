import os
import redis
import requests
from dotenv import load_dotenv

load_dotenv()

# Load secrets
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")  # Make sure this is set in your .env
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Connect to Redis
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

def store_token():
    token = get_token()
    r.set("oauth_token", token, ex=900)  # 900 seconds = 15 minutes
    print("Token stored in Redis for 15 minutes.")


def send_mock_request():
    token = r.get("oauth_token")
    if not token:
        print("No token found in Redis. Exiting.")
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
    print(response.json())



if __name__ == "__main__":
    store_token()
    send_mock_request()
