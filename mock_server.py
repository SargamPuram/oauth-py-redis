from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

fake = Faker()

app = Flask(__name__)

MOCK_TOKEN = "mock_token_123"  # Simulated token to check auth

@app.route("/register/<registerType>/<arsId>", methods=["POST"])
def register(registerType, arsId):
    # --- Extract and Validate Headers ---
    auth_header = request.headers.get("Authorization", "")
    correlation_id = request.headers.get("CorrelationId")
    client_name_header = request.headers.get("ClientName")

    if not auth_header.startswith("Bearer ") or auth_header.split(" ")[1] != MOCK_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    if not correlation_id or not client_name_header:
        return jsonify({"error": "Missing required headers"}), 400

    # --- Validate Path Param ---
    if registerType != "verified-identity":
        return jsonify({"error": "Invalid registerType"}), 400

    # --- Validate Request Body ---
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

    # --- Construct Mock Response ---
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