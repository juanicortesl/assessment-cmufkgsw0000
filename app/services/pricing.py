"""
Servicio de calculo de aranceles y tarifas de gestion notarial.
"""

BASE_FEES = {
    "PODER_ESPECIAL": 14990,
    "PODER_GENERAL": 24990,
    "DECLARACION_JURADA": 9990,
}

URGENCY_SURCHARGE = 4000


def calculate_deed_fee(deed_type: str, urgent: bool = True) -> int:
    """
    Calcula el costo total del tramite notarial considerando recargo por atencion prioritaria.
    """
    base = BASE_FEES.get(deed_type, 14990)
    if urgent:
        return base + URGENCY_SURCHARGE
    return base
