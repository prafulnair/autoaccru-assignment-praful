from app import crud, schemas
from . import factories


def test_create_patient_marks_new(db_session):
    payload = factories.patient_payload(first_name="Alice", last_name="Nguyen")
    patient_in = schemas.PatientCreate(**payload)

    saved = crud.create_patient(db_session, patient_in)

    assert saved.id is not None
    assert saved.new_patient is True
    assert saved.first_name == "Alice"


def test_create_patient_deduplicates_by_phone(db_session):
    payload = factories.patient_payload(phone_number="5145559999")
    patient_in = schemas.PatientCreate(**payload)
    first = crud.create_patient(db_session, patient_in)

    updated_payload = payload | {"address": "500 Updated Rd"}
    updated_in = schemas.PatientCreate(**updated_payload)
    second = crud.create_patient(db_session, updated_in)

    assert second.id == first.id
    assert second.new_patient is False
    assert second.address == "500 Updated Rd"


def test_list_patients_orders_by_newest(db_session):
    older = factories.create_patient(db_session, first_name="Older")
    newer = factories.create_patient(db_session, first_name="Newer")

    results = crud.list_patients(db_session)

    assert results[0].id == newer.id
    assert results[1].id == older.id
