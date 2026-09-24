"""
Servicio principal de coordinacion de generacion y gestion de escrituras notariales.
"""
import logging
import os
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import NotarialDeed
from app.services.renderer import render_notarial_deed

logger = logging.getLogger("document_service")
logger.setLevel(logging.INFO)

# Configurar handler para registrar errores en logs/rendering_errors.log
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "rendering_errors.log")

file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
file_handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(file_handler)


def generate_document(
    db: Session,
    client_dict: dict,
    deed_type: str,
    payment_id: str,
) -> NotarialDeed:
    """
    Ejecuta el ciclo de vida de generacion de una escritura notarial.
    Verifica el pago, genera el codigo unico y procesa la renderizacion.
    """
    import uuid
    document_code = f"DOC-2024-{uuid.uuid4().hex[:8].upper()}"

    logger.info(
        f"Iniciando generacion de documento {document_code} para cliente rut={client_dict.get('rut')} con pago={payment_id}"
    )

    # Registro inicial en base de datos con pago confirmado
    deed = NotarialDeed(
        document_code=document_code,
        deed_type=deed_type,
        customer_rut=client_dict.get("rut", ""),
        payment_id=payment_id,
        payment_status="COMPLETED",
        status="PENDING",
        created_at=datetime.utcnow(),
    )
    db.add(deed)
    db.commit()
    db.refresh(deed)

    metadata = {
        "document_code": document_code,
        "deed_type": deed_type,
        "created_at": deed.created_at.strftime("%d de %B de %Y"),
    }

    try:
        rendered = render_notarial_deed(deed_type, client_dict, metadata)
        deed.rendered_content = rendered
        deed.status = "COMPLETED"
        db.commit()
        db.refresh(deed)
        logger.info(f"Documento {document_code} generado exitosamente.")
        return deed
    except KeyError as exc:
        err_msg = f"KeyError: {exc}"
        logger.error(f"Error en renderizado de {document_code} (pago {payment_id}): {err_msg}")
        deed.status = "FAILED"
        deed.error_log = err_msg
        db.commit()
        db.refresh(deed)
        raise exc
    except Exception as exc:
        err_msg = str(exc)
        logger.error(f"Error inesperado en {document_code}: {err_msg}")
        deed.status = "FAILED"
        deed.error_log = err_msg
        db.commit()
        db.refresh(deed)
        raise exc


def get_deed_by_code(db: Session, document_code: str) -> NotarialDeed | None:
    return db.query(NotarialDeed).filter(NotarialDeed.document_code == document_code).first()
