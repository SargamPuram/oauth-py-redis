from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from faker import Faker
import jwt
import time

load_dotenv()

fake = Faker()

app = Flask(__name__)

MOCK_TOKEN = "mock_token_123"  # Simulated token to check auth

EXPECTED_AUDIENCE = "https://graph.microsoft.com"  # Replace with correct value if needed

# --- Decode and Validate JWT ---
def decode_and_validate_token(token):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False, "verify_aud": False}, algorithms=["RS256"])
        
        audience = decoded_token.get("aud")
        expiry = decoded_token.get("exp")

        if audience != EXPECTED_AUDIENCE:
            raise ValueError(f"Invalid audience: {audience}")

        current_time = int(time.time())
        if expiry < current_time:
            raise ValueError(f"Token expired at {expiry}")

        print("Token valid.")
        return decoded_token

    except Exception as e:
        print(f"JWT Validation Error: {e}")
        raise

# --- Routes ---
@app.route("/register/<registerType>/<arsId>", methods=["POST"])
def register(registerType, arsId):
    auth_header = request.headers.get("Authorization", "")
    correlation_id = request.headers.get("CorrelationId")
    client_name_header = request.headers.get("ClientName")

    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized - Missing Bearer token"}), 401

    token = auth_header.split(" ")[1]

    try:
        decode_and_validate_token(token)
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    if not correlation_id or not client_name_header:
        return jsonify({"error": "Missing required headers"}), 400

    if registerType != "verified-identity":
        return jsonify({"error": "Invalid registerType"}), 400

    body = request.get_json()
    if not body or "serviceAccessDataDetails" not in body:
        return jsonify({"error": "Missing serviceAccessDataDetails"}), 400

    details = body["serviceAccessDataDetails"]
    required_fields = [
        "clientName", "globalTransactionId", "recordRestricted", "registerAccessed",
        "requestId", "requestReason", "requestTimestamp", "requesterType", "subjectRegisterId"
    ]
    missing_fields = [field for field in required_fields if field not in details]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {missing_fields}"}), 400

    # --- Mock Response ---
    response = {
        "entryNumber": fake.random_int(min=100000, max=999999),
        "entryTimestamp": fake.time(pattern="%H:%M:%S:%f")[:-3],
        "registerKey": arsId,
        "personName": {
            "givenNames": fake.first_name(),
            "middleNames": fake.first_name(),
            "familyName": fake.last_name(),
            "nameInDispute": fake.boolean()
        },
        "personNameTransliterated": {
            "givenNamesTransliterated": fake.first_name(),
            "familyNameTransliterated": fake.last_name()
        },
        "gender": fake.random_element(elements=("Male", "Female")),
        "genderInDispute": fake.boolean(),
        "dateOfBirth": fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
        "dateOfBirthInDispute": fake.boolean(),
        "placeOfBirth": fake.city(),
        "placeOfBirthInDispute": fake.boolean(),
        "placeOfBirthTransliterated": fake.city(),
        "countryOfBirth": fake.country(),
        "countryOfBirthInDispute": fake.boolean(),
        "identityStatus": "Verified",
        "legacyId": f"LEG-{fake.year()}-{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}",
        "verificationDate": {
            "dateVerified": fake.date_this_decade().isoformat(),
            "expiryDate": fake.date_between(start_date="+1y", end_date="+10y").isoformat()
        }
    }

    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
