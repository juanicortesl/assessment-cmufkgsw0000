from datetime import datetime
from pydantic import BaseModel


class ClientData(BaseModel):
    rut: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    commune: str | None = None
    region: str | None = None
    estado_civil: str | None = None
    profesion_oficio: str | None = None


class GenerateDocumentRequest(BaseModel):
    client: ClientData
    deed_type: str = "PODER_ESPECIAL"
    payment_id: str


class GenerateDocumentResponse(BaseModel):
    document_code: str
    deed_type: str
    status: str
    payment_status: str
    rendered_content: str | None = None
    created_at: datetime


class DocumentStatusResponse(BaseModel):
    document_code: str
    deed_type: str
    status: str
    payment_status: str
    error_log: str | None = None
    created_at: datetime
