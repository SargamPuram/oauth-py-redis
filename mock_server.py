from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

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
        "entryNumber": 123456,
        "entryTimestamp": "12:34:56:78",
        "registerKey": arsId,
        "personName": {
            "givenNames": "Sargam",
            "middleNames": "N/A",
            "familyName": "Puram",
            "nameInDispute": False
        },
        "personNameTransliterated": {
            "givenNamesTransliterated": "Sargam",
            "familyNameTransliterated": "Puram"
        },
        "gender": "Female",
        "genderInDispute": False,
        "dateOfBirth": "2003-08-21",
        "dateOfBirthInDispute": False,
        "placeOfBirth": "Pune",
        "placeOfBirthInDispute": False,
        "placeOfBirthTransliterated": "Pune",
        "countryOfBirth": "India",
        "countryOfBirthInDispute": False,
        "identityStatus": "Verified",
        "legacyId": "LEG-2025-SG",
        "verificationDate": {
            "dateVerified": "2025-04-23",
            "expiryDate": "2030-04-23"
        }
    }

    return jsonify(response), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)