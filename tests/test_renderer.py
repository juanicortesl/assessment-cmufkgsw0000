from app.services.renderer import render_notarial_deed


def test_render_notarial_deed_interpolation():
    client_dict = {
        "rut": "15.342.198-4",
        "full_name": "Juan Pablo Morales Sepulveda",
        "email": "j.morales@example.cl",
        "address": "Av. Providencia 1240",
        "commune": "Providencia",
    }
    metadata = {
        "document_code": "DOC-2024-8841",
        "deed_type": "PODER_ESPECIAL",
        "created_at": "14 de octubre de 2024",
    }
    result = render_notarial_deed("PODER_ESPECIAL", client_dict, metadata)
    assert "Juan Pablo Morales Sepulveda" in result
