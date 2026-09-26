# INC-4092 — Emisión de poderes notariales restablecida

**Para:** Equipo de Operaciones Legales y Soporte al Cliente
**Canal:** `#incidencias-ops-legal`

---

Hola equipo:

Ya encontramos y corregimos el problema que impedía emitir los poderes notariales urgentes. Les explicamos qué pasó y qué necesitamos de ustedes para cerrar los casos de hoy.

## Qué pasó

El sistema armaba cada poder con el **estado civil** y la **profesión u oficio** del cliente, y exigía ambos datos. Algunos clientes tienen la ficha incompleta. Cuando el sistema intentaba emitir el documento de uno de ellos, se detenía y mostraba "Error interno del servidor", aunque el pago ya se había cobrado.

Por eso los errores parecían aleatorios: solo afectaban a los clientes con la ficha incompleta. Los demás clientes emitían sus documentos sin problema.

## Qué hicimos

1. **El sistema ya no se detiene.** Si falta el estado civil o la profesión, el poder se emite sin mencionar ese dato. Para la validez del poder ante notaría basta con el nombre completo, el RUT y el domicilio, así que el documento queda listo para firmar.
2. **No hay documentos duplicados.** Si alguien reintenta la emisión de un pago que ya se cobró, el sistema reutiliza el mismo documento y no genera uno nuevo.
3. **Recuperamos los documentos que fallaron.** Volvemos a procesar los documentos cobrados que quedaron en "Error", sin cobrar de nuevo al cliente.

## Qué necesitamos de ustedes

- **Avísennos si algún documento sigue en "Error"** después del reprocesamiento. Serán casos puntuales, por ejemplo un cliente que no está registrado, y los revisaremos uno por uno.
- **No es necesario pedirles datos adicionales a los clientes** para emitir estos poderes.

Casos prioritarios de hoy, que se procesan primero:

| Documento | Cliente | Cita |
|---|---|---|
| DOC-2024-8849 | María González T. | 13:00 |
| DOC-2024-8841 | Juan Morales S. | 14:00 |
| DOC-2024-8853 | Carlos Henríquez P. | 15:30 |
| DOC-2024-8858 | Patricia Fuenzalida | 16:00 |

## Qué pueden decirle a los clientes

> "Tuvimos un problema técnico al generar su documento, que ya está resuelto. Su pago está registrado correctamente y no se le volverá a cobrar. Su poder ya está disponible para la firma."

Cualquier duda, estamos en este canal.

— Equipo de Ingeniería
