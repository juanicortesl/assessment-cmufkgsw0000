"""
Servicio principal de coordinacion de generacion y gestion de escrituras notariales.
"""
import logging
import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Client, NotarialDeed
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

SPANISH_MONTHS = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)

CLIENT_FIELDS = (
    "rut", "full_name", "email", "phone", "address",
    "commune", "region", "estado_civil", "profesion_oficio",
)


def format_spanish_date(value: datetime) -> str:
    # strftime("%B") depende del locale del servidor y emitia meses en ingles.
    return f"{value.day} de {SPANISH_MONTHS[value.month - 1]} de {value.year}"


def generate_document(
    db: Session,
    client_dict: dict,
    deed_type: str,
    payment_id: str,
) -> NotarialDeed:
    """
    Ejecuta el ciclo de vida de generacion de una escritura notarial.
    Es idempotente por payment_id: un reintento sobre un pago ya cobrado reutiliza
    su escritura en vez de crear una nueva.
    """
    deed = get_deed_by_payment(db, payment_id)

    if deed is not None and deed.status == "COMPLETED":
        logger.info(f"Pago {payment_id} ya tiene documento emitido {deed.document_code}; se reutiliza.")
        return deed

    if deed is None:
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
    else:
        logger.info(f"Reprocesando documento {deed.document_code} (estado {deed.status}) para pago={payment_id}")
        deed.deed_type = deed_type

    return render_into_deed(db, deed, client_dict)


def render_into_deed(db: Session, deed: NotarialDeed, client_dict: dict) -> NotarialDeed:
    """
    Renderiza la escritura y persiste el resultado sobre el registro existente.
    """
    metadata = {
        "document_code": deed.document_code,
        "deed_type": deed.deed_type,
        "created_at": format_spanish_date(deed.created_at),
    }

    try:
        rendered = render_notarial_deed(deed.deed_type, client_dict, metadata)
        deed.rendered_content = rendered
        deed.status = "COMPLETED"
        deed.error_log = None
        db.commit()
        db.refresh(deed)
        logger.info(f"Documento {deed.document_code} generado exitosamente.")
        return deed
    except KeyError as exc:
        err_msg = f"KeyError: {exc}"
        logger.error(f"Error en renderizado de {deed.document_code} (pago {deed.payment_id}): {err_msg}")
        deed.status = "FAILED"
        deed.error_log = err_msg
        db.commit()
        db.refresh(deed)
        raise exc
    except Exception as exc:
        err_msg = str(exc)
        logger.error(f"Error inesperado en {deed.document_code}: {err_msg}")
        deed.status = "FAILED"
        deed.error_log = err_msg
        db.commit()
        db.refresh(deed)
        raise exc


def reprocess_failed_deeds(db: Session, apply: bool = False) -> list[dict]:
    """
    Reprocesa escrituras cobradas que quedaron en FAILED, usando la ficha del cliente.
    Por pago se reprocesa solo el intento mas reciente; si el pago ya tiene una escritura
    emitida, se omite. Con apply=False solo reporta lo que haria.
    """
    failed = (
        db.query(NotarialDeed)
        .filter(NotarialDeed.status == "FAILED", NotarialDeed.payment_status == "COMPLETED")
        .order_by(NotarialDeed.created_at.desc(), NotarialDeed.id.desc())
        .all()
    )

    results = []
    seen_payments = set()
    for deed in failed:
        result = {"document_code": deed.document_code, "payment_id": deed.payment_id}
        if deed.payment_id in seen_payments:
            results.append({**result, "action": "skipped", "reason": "intento duplicado del mismo pago"})
            continue
        seen_payments.add(deed.payment_id)

        if get_deed_by_payment(db, deed.payment_id).status == "COMPLETED":
            results.append({**result, "action": "skipped", "reason": "el pago ya tiene documento emitido"})
            continue

        client = db.query(Client).filter(Client.rut == deed.customer_rut).first()
        if client is None:
            results.append({**result, "action": "skipped", "reason": f"cliente {deed.customer_rut} no existe"})
            continue

        client_dict = {
            field: getattr(client, field)
            for field in CLIENT_FIELDS
            if getattr(client, field) is not None
        }
        if not apply:
            results.append({**result, "action": "would_reprocess"})
            continue

        try:
            render_into_deed(db, deed, client_dict)
            results.append({**result, "action": "reprocessed"})
        except Exception as exc:
            results.append({**result, "action": "failed", "reason": str(exc)})

    return results


def get_deed_by_payment(db: Session, payment_id: str) -> NotarialDeed | None:
    """
    Retorna la escritura vigente de un pago: la emitida si existe, si no el intento mas reciente.
    """
    deeds = (
        db.query(NotarialDeed)
        .filter(NotarialDeed.payment_id == payment_id)
        .order_by(NotarialDeed.created_at.desc(), NotarialDeed.id.desc())
        .all()
    )
    for deed in deeds:
        if deed.status == "COMPLETED":
            return deed
    return deeds[0] if deeds else None


def get_deed_by_code(db: Session, document_code: str) -> NotarialDeed | None:
    return db.query(NotarialDeed).filter(NotarialDeed.document_code == document_code).first()
