"""
Modulo de renderizado de escrituras y mandatos notariales para Total Abogados.
Genera el contenido formal de los documentos legales interpolando los datos de comparecencia.
"""

TEMPLATES = {
    "PODER_ESPECIAL": (
        "ESCRITURA PUBLICA DE PODER ESPECIAL NOTARIAL\n"
        "CODIGO: {codigo_documento}\n"
        "En Santiago de Chile, a {fecha_emision}, comparece don/dona {cliente_nombre}, "
        "cedula de identidad numero {cliente_rut}, de nacionalidad {cliente_nacionalidad}, "
        "estado civil {cliente_estado_civil}, profesion u oficio {cliente_profesion}, "
        "domiciliado/a en {cliente_domicilio}, comuna de {cliente_comuna}, quien confiere "
        "poder especial suficiente a Total Abogados SpA para representarle en tramites y "
        "gestiones notariales pertinentes."
    ),
    "PODER_GENERAL": (
        "ESCRITURA PUBLICA DE PODER GENERAL Y JUDICIAL\n"
        "CODIGO: {codigo_documento}\n"
        "En Santiago de Chile, comparece don/dona {cliente_nombre}, cedula de identidad {cliente_rut}, "
        "estado civil {cliente_estado_civil}, de profesion u oficio {cliente_profesion}, "
        "domiciliado/a en {cliente_domicilio}, comuna de {cliente_comuna}, quien confiere poder amplio..."
    ),
}

# Datos de comparecencia que pueden venir vacios (p. ej. clientes migrados sin ficha completa).
# Se dejan como linea en blanco para completarse en notaria en vez de abortar la emision.
OPTIONAL_APPEARANCE_FIELDS = ("estado_civil", "profesion_oficio")
MISSING_FIELD_PLACEHOLDER = "____________________"


def find_missing_fields(client_data: dict) -> list[str]:
    """
    Retorna los datos de comparecencia opcionales que no vienen informados.
    """
    return [field for field in OPTIONAL_APPEARANCE_FIELDS if not client_data.get(field)]


def build_document_context(client_data: dict, deed_metadata: dict) -> dict:
    """
    Construye el mapa de variables requeridas para la plantilla notarial.
    Estructura la informacion del compareciente y los datos de la escritura.
    """
    context = {
        "codigo_documento": deed_metadata.get("document_code", "DOC-DRAFT"),
        "tipo_tramite": deed_metadata.get("deed_type", "PODER_ESPECIAL"),
        "fecha_emision": deed_metadata.get("created_at", "14 de octubre de 2024"),
        "cliente_nombre": client_data["full_name"],
        "cliente_rut": client_data["rut"],
        "cliente_email": client_data.get("email", ""),
        "cliente_domicilio": client_data.get("address", "Santiago"),
        "cliente_comuna": client_data.get("commune", "Santiago"),
        "cliente_nacionalidad": client_data.get("nacionalidad", "chilena"),
        "cliente_estado_civil": client_data.get("estado_civil") or MISSING_FIELD_PLACEHOLDER,
        "cliente_profesion": client_data.get("profesion_oficio") or MISSING_FIELD_PLACEHOLDER,
    }
    return context


def interpolate_variables(template_str: str, variables: dict) -> str:
    """
    Ejecuta la sustitucion de las variables en la plantilla formal.
    """
    return template_str.format(**variables)


def render_notarial_deed(deed_type: str, client_data: dict, deed_metadata: dict) -> str:
    """
    Coordina la obtencion de la plantilla y la renderizacion con los datos del cliente.
    """
    template = TEMPLATES.get(deed_type, TEMPLATES["PODER_ESPECIAL"])
    context = build_document_context(client_data, deed_metadata)
    return interpolate_variables(template, context)
