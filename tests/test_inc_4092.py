"""
Regresiones del incidente INC-4092: clientes sin estado civil o profesion u oficio
provocaban KeyError y HTTP 500 despues de cobrar.
"""
import uuid
from datetime import datetime

from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.models import Client, NotarialDeed
from app.services import document_service
from app.services.renderer import MISSING_FIELD_PLACEHOLDER, render_notarial_deed


def _unique_payment() -> str:
    return f"tx_test_{uuid.uuid4().hex[:10]}"


def _unique_rut() -> str:
    return f"TEST-{uuid.uuid4().hex[:8]}"


METADATA = {
    "document_code": "DOC-2024-8849",
    "deed_type": "PODER_ESPECIAL",
    "created_at": "14 de octubre de 2024",
}


def test_render_without_estado_civil_leaves_blank_line():
    client_dict = {"rut": "15.342.198-4", "full_name": "Juan Morales S.", "profesion_oficio": "Contador"}
    result = render_notarial_deed("PODER_ESPECIAL", client_dict, METADATA)
    assert f"estado civil {MISSING_FIELD_PLACEHOLDER}" in result
    assert "profesion u oficio Contador" in result


def test_render_without_profesion_leaves_blank_line():
    client_dict = {"rut": "12.000.000-0", "full_name": "Maria Gonzalez T.", "estado_civil": "Casada"}
    result = render_notarial_deed("PODER_GENERAL", client_dict, METADATA)
    assert "estado civil Casada" in result
    assert f"profesion u oficio {MISSING_FIELD_PLACEHOLDER}" in result


def test_endpoint_with_null_fields_returns_200_and_flags_missing_data(client: TestClient):
    payload = {
        "client": {"rut": _unique_rut(), "full_name": "Cliente Migrado", "estado_civil": None, "profesion_oficio": None},
        "payment_id": _unique_payment(),
    }
    response = client.post("/documents/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"

    status = client.get(f"/documents/{data['document_code']}/status").json()
    assert "estado_civil" in status["error_log"]
    assert "profesion_oficio" in status["error_log"]


def test_complete_client_has_no_pending_data_and_spanish_date(client: TestClient):
    payload = {
        "client": {
            "rut": _unique_rut(),
            "full_name": "Cliente Completo",
            "estado_civil": "Soltera",
            "profesion_oficio": "Abogada",
        },
        "payment_id": _unique_payment(),
    }
    data = client.post("/documents/generate", json=payload).json()
    status = client.get(f"/documents/{data['document_code']}/status").json()
    assert status["error_log"] is None
    month = document_service.SPANISH_MONTHS[datetime.utcnow().month - 1]
    assert f" de {month} de " in data["rendered_content"]


def test_retry_same_payment_reuses_deed_instead_of_creating_new_one():
    db = SessionLocal()
    payment_id = _unique_payment()
    try:
        client_dict = {"rut": _unique_rut(), "full_name": "Cliente Reintento"}
        first = document_service.generate_document(db, client_dict, "PODER_ESPECIAL", payment_id)
        second = document_service.generate_document(db, client_dict, "PODER_ESPECIAL", payment_id)
        assert first.document_code == second.document_code
        assert db.query(NotarialDeed).filter(NotarialDeed.payment_id == payment_id).count() == 1
    finally:
        db.close()


def test_reprocess_failed_deed_recovers_it_from_client_record():
    db = SessionLocal()
    rut = _unique_rut()
    payment_id = _unique_payment()
    try:
        db.add(Client(rut=rut, full_name="Cliente Fallido", estado_civil=None, profesion_oficio="Contador", is_migrated=True))
        older = NotarialDeed(
            document_code=f"DOC-2024-{uuid.uuid4().hex[:8].upper()}",
            customer_rut=rut, payment_id=payment_id, status="FAILED",
            error_log="KeyError: 'estado_civil'", created_at=datetime(2024, 10, 14, 12, 0),
        )
        latest = NotarialDeed(
            document_code=f"DOC-2024-{uuid.uuid4().hex[:8].upper()}",
            customer_rut=rut, payment_id=payment_id, status="FAILED",
            error_log="KeyError: 'estado_civil'", created_at=datetime(2024, 10, 14, 12, 5),
        )
        db.add_all([older, latest])
        db.commit()

        dry_run = [r for r in document_service.reprocess_failed_deeds(db) if r["payment_id"] == payment_id]
        assert [r["action"] for r in dry_run] == ["would_reprocess", "skipped"]
        db.refresh(latest)
        assert latest.status == "FAILED"

        applied = [r for r in document_service.reprocess_failed_deeds(db, apply=True) if r["payment_id"] == payment_id]
        assert applied[0] == {
            "document_code": latest.document_code,
            "payment_id": payment_id,
            "action": "reprocessed",
            "missing_fields": ["estado_civil"],
        }
        db.refresh(latest)
        db.refresh(older)
        assert latest.status == "COMPLETED"
        assert "Cliente Fallido" in latest.rendered_content
        assert older.status == "FAILED"
    finally:
        db.close()
