from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.services import document_service


def test_generate_power_of_attorney_deed_execution(client: TestClient):
    payload = {
        "client": {
            "rut": "15.342.198-4",
            "full_name": "Juan Pablo Morales Sepulveda",
            "email": "j.morales@example.cl",
            "address": "Av. Providencia 1240",
            "commune": "Providencia",
        },
        "deed_type": "PODER_ESPECIAL",
        "payment_id": "tx_pay_902148",
    }
    response = client.post("/documents/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["payment_status"] == "COMPLETED"


def test_document_service_generates_completed_deed():
    db = SessionLocal()
    try:
        client_dict = {
            "rut": "15.342.198-4",
            "full_name": "Juan Pablo Morales Sepulveda",
            "email": "j.morales@example.cl",
            "address": "Av. Providencia 1240",
            "commune": "Providencia",
        }
        deed = document_service.generate_document(
            db=db,
            client_dict=client_dict,
            deed_type="PODER_ESPECIAL",
            payment_id="tx_pay_902148",
        )
        assert deed.status == "COMPLETED"
    finally:
        db.close()


def test_generate_power_of_attorney_standard_customer(client: TestClient):
    payload = {
        "client": {
            "rut": "18.234.567-8",
            "full_name": "Francisca Andrea Silva Castro",
            "email": "f.silva@example.cl",
            "address": "Los Leones 1500",
            "commune": "Providencia",
            "estado_civil": "Soltera",
            "profesion_oficio": "Ingeniera Comercial",
        },
        "deed_type": "PODER_ESPECIAL",
        "payment_id": "tx_pay_902199",
    }
    response = client.post("/documents/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert "Francisca Andrea Silva Castro" in data["rendered_content"]
