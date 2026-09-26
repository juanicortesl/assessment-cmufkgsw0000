# Informe técnico — INC-4092

**Servicio:** `document-rendering-service` · **Severidad:** P1 · **Fecha del incidente:** 14-oct-2024

## 1. Resumen

Desde las 08:45 CLT, `POST /documents/generate` respondía HTTP 500 a una parte de los clientes, con el pago ya cobrado. La causa es un `KeyError` en el renderer cuando el cliente no tiene `estado_civil` o `profesion_oficio`. Los fallos parecían aleatorios porque dependían de los datos de cada cliente y no de la carga ni de la hora. Se corrigió el renderer, se hizo idempotente la emisión por pago y se agregó un script para reprocesar los documentos fallidos.

## 2. Causa raíz

```
Cliente sin estado_civil / profesion_oficio (columnas nullable en clients; perfil de clientes migrados)
  └─► router: payload.client.model_dump(exclude_none=True)   → la key desaparece del dict
        └─► renderer.build_document_context: client_data["estado_civil"]  → KeyError
              └─► router captura KeyError → HTTP 500
```

- `app/services/renderer.py` accedía con `[]` a dos campos que el esquema (`ClientData`) y el modelo (`Client`) declaran **opcionales**. El resto de los campos opcionales usaba `.get()` con un valor por defecto. Es un contrato roto entre la entrega del proveedor y el modelo de datos.
- **Evidencia en el log** (`logs/rendering_errors.log`): `DOC-2024-8841` → `KeyError: 'estado_civil'`, y `DOC-2024-8849` → `KeyError: 'profesion_oficio'`. En la misma ventana, `DOC-8835` y `DOC-8845` se emitieron sin problema.
- **Reproducción local:** con un cliente completo → 200. Sin estado civil, sin profesión o con ambos en `null` → 500. Además, 3 de los 6 tests del repo ya fallaban por esta causa (`test_generate_power_of_attorney_deed_execution`, `test_document_service_generates_completed_deed`, `test_render_notarial_deed_interpolation`).

### Factores que agravaron el impacto

| Factor | Efecto |
|---|---|
| El deed se persiste con `payment_status=COMPLETED` **antes** de renderizar | El cliente queda cobrado con el documento en `FAILED` |
| Sin idempotencia por `payment_id` | Cada reintento desde el panel crea un deed nuevo. Reproducido: `tx_pay_902148` quedó con 2 deeds fallidos |
| El log registra solo el **primer** campo faltante | No se puede saber desde el log si a Juan Morales también le falta la profesión |
| `strftime("%B")` depende del locale | La fecha de la escritura salía en inglés ("26 de September de 2026") |

### Limitaciones de la investigación

- El repositorio tiene un único commit (`Initial commit`). No se puede fechar el cambio del proveedor ni ver el código anterior.
- No hubo acceso a la BD ni a los logs de producción. El ticket reporta 14 casos entre 08:30 y 09:10, pero el log solo contiene 2 errores, ambos posteriores a las 09:10. El log disponible está incompleto: puede haber varias instancias o un archivo local que se pierde con cada deploy.
- El mail que mencionaba "limpieza de tablas" en `tests/conftest.py` no coincide con el repositorio: la fixture no limpia nada.

## 3. Solución implementada

| Cambio | Archivo |
|---|---|
| `estado_civil` y `profesion_oficio` se leen con `.get()`. Si faltan, se imprime una línea en blanco (`MISSING_FIELD_PLACEHOLDER`) para completar en notaría. `full_name` y `rut` siguen siendo obligatorios | `app/services/renderer.py` |
| `find_missing_fields()` detecta los datos faltantes. El deed queda `COMPLETED` y `error_log` indica qué completar, visible en `GET /documents/{code}/status` | `renderer.py`, `document_service.py` |
| **Idempotencia por `payment_id`:** si el pago ya tiene un deed emitido, se devuelve ese. Si tiene uno fallido, se reprocesa el mismo registro sin crear otro | `app/services/document_service.py` |
| Fecha en español, sin depender del locale (`format_spanish_date`) | `document_service.py` |
| `reprocess_failed_deeds()` y su CLI: toma los deeds `FAILED` con pago `COMPLETED`, reprocesa solo el intento más reciente de cada pago, reconstruye los datos desde `clients` y **por defecto corre en dry-run** | `document_service.py`, `scripts/reprocess_failed_deeds.py` |
| 6 tests de regresión: campos faltantes, `null` explícito, fecha en español, idempotencia, reprocesamiento con dry-run y apply | `tests/test_inc_4092.py` |

**Por qué una línea en blanco y no rechazar con 422.** Los tests existentes esperan `COMPLETED` para un cliente sin esos campos. La operación necesitaba un borrador ese mismo día, y Legal se ofreció a validarlo. La línea en blanco no inventa datos legales, porque el dato se completa en notaría, y el `error_log` deja trazabilidad. La alternativa, validar antes de cobrar y responder 422, es más estricta, pero habría dejado sin documento a los clientes que ya estaban en la notaría.

**Verificación:** `pytest` → 13/13, repetible en dos corridas seguidas sobre la misma BD. En una BD que simula el incidente, el script recupera `DOC-2024-8841` y `DOC-2024-8849` y omite `DOC-2024-8853` porque su cliente no existe.

**Sin impacto en la operación en curso:** no hay cambios de esquema ni migraciones, la API mantiene su contrato y el script no escribe nada sin `--apply`.

**Runbook de recuperación:**
```bash
python -m scripts.reprocess_failed_deeds            # 1. revisar el reporte
python -m scripts.reprocess_failed_deeds --apply    # 2. aplicar
```

## 4. Riesgos de infraestructura y dependencias detectados

| # | Riesgo | Evidencia | Recomendación |
|---|---|---|---|
| 1 | **Credenciales de producción en el repo** | `VENDOR_SHARED_API_KEY=ld_vendor_shared_live_…` y `VENDOR_SHARED_SECRET` en `.env.example` y como valor por defecto en `app/config.py` | **Rotarlas ya**: siguen en el historial de git. Quitar los defaults y cargarlas desde un gestor de secretos. Además, la credencial es "shared", compartida con el proveedor |
| 2 | **Hash de documento no determinístico** | `notary_client.py` usa `str(hash(content))`. Con `PYTHONHASHSEED` aleatorio da un valor distinto en cada proceso (verificado: 3 corridas, 3 hashes distintos) | Usar `hashlib.sha256`. Con el código actual, la notaría no puede verificar la integridad del documento |
| 3 | El token del partner viaja en el cuerpo del payload (`partner_token`) | `prepare_certification_payload` | Moverlo a un header de autenticación y no loguear payloads |
| 4 | Timeout de 30 s con la notaría externa, sin reintentos ni circuit breaker | `NOTARY_PARTNER_TIMEOUT_SECONDS=30` | En emisiones urgentes, un proveedor lento bloquea workers. Bajar el timeout y encolar la certificación |
| 5 | Cobro confirmado antes de generar el documento | `payment_status="COMPLETED"` al crear el deed | Validar los datos antes del cobro, o bien capturar el pago solo cuando el documento esté emitido |
| 6 | Logs en un archivo local versionado, con RUT (dato personal) | `logs/rendering_errors.log` está en git. Los tests escriben en él | Loguear a stdout hacia un agregador, sacar `logs/` del repo y enmascarar el RUT |
| 7 | Esquema creado con `create_all` al importar y sin migraciones | `app/main.py`; `alembic/versions/` no existe | Generar la migración inicial y aplicar el esquema con Alembic en el deploy |
| 8 | Dependencias sin versión fija | `requirements.txt` usa solo `>=` | Usar un lockfile. Hoy `starlette` ya emite una deprecación de `httpx` en los tests |
| 9 | Los tests comparten `local.db` sin aislamiento | `tests/conftest.py` | Crear una BD temporal por sesión de tests. Los tests nuevos usan IDs únicos para no depender del estado |

## 5. Próximos pasos

1. Rotar las credenciales del proveedor (riesgo 1). Es lo más urgente y no depende de este PR.
2. Deploy del fix y ejecución del script en dry-run sobre producción. Revisar el resultado con Operaciones y luego correr `--apply`.
3. Enviar a Legal la lista de clientes con datos pendientes (`error_log` con "Datos pendientes") y completar esas fichas en `clients`.
4. Corregir el hash de certificación (riesgo 2) antes de la siguiente entrega del proveedor.
