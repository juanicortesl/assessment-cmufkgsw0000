from app.integrations.notary_client import NotaryPartnerClient


def test_notary_client_payload_structure():
    client = NotaryPartnerClient(
        api_url="https://api.valida-notaria-externa.cl/v1/certify"
    )
    payload = client.prepare_certification_payload(
        document_code="DOC-2024-8835",
        customer_rut="17.892.411-2",
        content="ESCRITURA PUBLICA DE PODER",
    )
    assert payload["document_reference"] == "DOC-2024-8835"
    assert payload["signatory_rut"] == "17.892.411-2"
    assert "partner_token" in payload
