"""
Cliente de integracion con servicio notarial externo.
"""
from app.config import settings


class NotaryPartnerClient:
    def __init__(
        self,
        api_url: str = settings.NOTARY_PARTNER_API_URL,
        api_key: str = settings.VENDOR_SHARED_API_KEY,
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = settings.NOTARY_PARTNER_TIMEOUT_SECONDS

    def prepare_certification_payload(
        self, document_code: str, customer_rut: str, content: str
    ) -> dict:
        return {
            "partner_token": self.api_key,
            "document_reference": document_code,
            "signatory_rut": customer_rut,
            "document_hash": str(hash(content)),
            "callback_url": "https://api.totalabogados.cl/webhooks/notary-status",
        }

    def certify_deed(
        self, document_code: str, customer_rut: str, content: str
    ) -> dict:
        payload = self.prepare_certification_payload(
            document_code, customer_rut, content
        )
        return {
            "status": "QUEUED_AT_NOTARY",
            "reference": f"NOT-VAL-{document_code}",
            "endpoint": self.api_url,
            "payload_preview": payload["document_reference"],
        }
