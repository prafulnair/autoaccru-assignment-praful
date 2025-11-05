from fastapi import status

from app import models
from app.demo_data import seed_demo_patients
from . import factories


def test_get_patients_returns_seed(db_session, client):
    seed_demo_patients(db_session)

    response = client.get("/patients")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body) == 3
    assert body[0]["first_name"] == "Sofia"  # newest first


def test_post_patients_creates_record(client):
    payload = factories.patient_payload()

    response = client.post("/patients", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["phone_number"] == payload["phone_number"]
    assert body["new_patient"] is True


def test_post_patients_returns_existing_on_duplicate_phone(client, db_session):
    payload = factories.patient_payload(phone_number="4385557777")
    client.post("/patients", json=payload)

    updated = payload | {"address": "200 Updated Blvd"}
    response = client.post("/patients", json=updated)

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["address"] == "200 Updated Blvd"
    assert body["new_patient"] is False

    stored = db_session.query(models.PatientTable).all()
    assert len(stored) == 1
