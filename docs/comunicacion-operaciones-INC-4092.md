# INC-4092 — Emisión de poderes notariales restablecida

**Para:** Equipo de Operaciones Legales y Soporte al Cliente
**Canal:** `#incidencias-ops-legal`

---

Hola equipo:

Ya encontramos y corregimos el problema que impedía emitir los poderes notariales urgentes. Les explicamos qué pasó y qué necesitamos de ustedes para cerrar los casos de hoy.

## Qué pasó

Un poder notarial necesita el **estado civil** y la **profesión u oficio** de quien comparece. Algunos clientes tienen la ficha incompleta, sin uno o ambos datos. Cuando el sistema intentaba armar el documento de uno de esos clientes, se detenía y mostraba "Error interno del servidor", aunque el pago ya se había cobrado.

Por eso los errores parecían aleatorios: solo afectaban a los clientes con la ficha incompleta. Los demás clientes emitían sus documentos sin problema.

## Qué hicimos

1. **El sistema ya no se detiene.** Si falta alguno de esos datos, el documento se emite igual y deja una **línea en blanco** (`____________________`) para completarla a mano en la notaría. En el panel, el documento indica qué dato quedó pendiente.
2. **No hay cobros dobles.** Si alguien reintenta la emisión de un pago que ya se cobró, el sistema reutiliza el mismo documento y no genera uno nuevo.
3. **Recuperamos los documentos que fallaron.** Volvemos a procesar los documentos cobrados que quedaron en "Error", sin cobrar de nuevo al cliente.

## Qué necesitamos de ustedes

- **Revisen las líneas en blanco antes de enviar a notaría.** Los documentos recuperados pueden traer el estado civil o la profesión sin completar.
- **Confirmen esos datos con cada cliente**, idealmente contra su cédula de identidad. Pueden completarse en la notaría o avisarnos para regenerar el documento con los datos ya incluidos.

Casos prioritarios de hoy:

| Documento | Cliente | Dato a confirmar | Cita |
|---|---|---|---|
| DOC-2024-8849 | María González T. | Profesión u oficio | 13:00 |
| DOC-2024-8841 | Juan Morales S. | Estado civil y profesión u oficio | 14:00 |
| DOC-2024-8853 | Carlos Henríquez P. | Por confirmar | 15:30 |
| DOC-2024-8858 | Patricia Fuenzalida | Por confirmar | 16:00 |

Para los otros 10 casos, les enviaremos la lista con el dato que falta en cada uno apenas termine el reprocesamiento.

## Qué pueden decirle a los clientes

> "Tuvimos un problema técnico al generar su documento, que ya está resuelto. Su pago está registrado correctamente y no se le volverá a cobrar. Para terminar su poder necesitamos confirmar su estado civil y su profesión u oficio."

Cualquier duda, estamos en este canal.

— Equipo de Ingeniería
