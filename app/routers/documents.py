from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import (
    DocumentStatusResponse,
    GenerateDocumentRequest,
    GenerateDocumentResponse,
)
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/generate",
    response_model=GenerateDocumentResponse,
    status_code=status.HTTP_200_OK,
)
def generate_document_endpoint(
    payload: GenerateDocumentRequest,
    db: Session = Depends(get_db),
):
    """
    Endpoint para emision de poderes y escrituras notariales urgentes.
    """
    client_dict = payload.client.model_dump(exclude_none=True)
    try:
        deed = document_service.generate_document(
            db=db,
            client_dict=client_dict,
            deed_type=payload.deed_type,
            payment_id=payload.payment_id,
        )
        return GenerateDocumentResponse(
            document_code=deed.document_code,
            deed_type=deed.deed_type,
            status=deed.status,
            payment_status=deed.payment_status,
            rendered_content=deed.rendered_content,
            created_at=deed.created_at,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en interpolacion de variables de plantilla: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fallo en emision de documento: {str(exc)}",
        )


@router.get(
    "/{document_code}/status",
    response_model=DocumentStatusResponse,
    status_code=status.HTTP_200_OK,
)
def get_document_status_endpoint(
    document_code: str,
    db: Session = Depends(get_db),
):
    deed = document_service.get_deed_by_code(db, document_code)
    if not deed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado",
        )
    return DocumentStatusResponse(
        document_code=deed.document_code,
        deed_type=deed.deed_type,
        status=deed.status,
        payment_status=deed.payment_status,
        error_log=deed.error_log,
        created_at=deed.created_at,
    )
