# Incidencia INC-4092: Falla critica en generacion de escrituras y poderes notariales urgentes

**Fecha de apertura:** 14 de octubre de 2024, 09:22 CLT  
**Severidad:** P1 - Critica (Operacion detenida)  
**Servicio impactado:** `document-rendering-service`  
**Canal de coordinacion:** Slack `#incidencias-ops-legal`  
**Estado:** Abierto / En investigacion  

---

## 1. Resumen del Incidente

A partir de las 08:45 AM, el equipo de Operaciones Legales comenzo a registrar multiples errores en la plataforma al intentar emitir escrituras publicas y poderes notariales urgentes solicitados por clientes. 

Los clientes reportan que, luego de completar exitosamente el pago a traves de la pasarela de pagos (Webpay / Flow), el sistema queda en estado pendiente y al forzar la descarga o regeneracion desde el panel operativo se visualiza una respuesta de error interno (HTTP 500). Esto esta impidiendo la entrega oportuna de poderes para tramites notariales programados para el dia de hoy.

---

## 2. Registro de Mensajes de Coordinacion (Slack / Operaciones Legales)

### [09:05 CLT] Lider de Operaciones Legales:
> Equipo de Ingenieria, buenos dias. Les escribo con caracter de extrema urgencia por este canal. Estamos teniendo una situacion critica con los poderes notariales urgentes.
> 
> Tenemos actualmente a tres clientes fisicamente presentes en la Notaria Camilo Valenzuela en Providencia (entre ellos don Juan Morales, ticket #4412, escritura `DOC-2024-8841`) esperando que les llegue el documento para firmar un alzamiento de hipoteca que vence hoy a las 14:00 horas. El notario no los va a esperar si no presentamos el borrador antes del mediodia.
> 
> En la plataforma de operaciones les aparece error 500 y no nos deja emitir el PDF. Por favor, alguien puede revisar que paso con el generador de documentos?

### [09:12 CLT] Especialista de Soporte al Cliente:
> Me sumo a la alerta. En Zendesk estamos colapsados de llamados y mensajes por WhatsApp. Los clientes nos dicen que la tarjeta ya les cobro los $18.990 correspondientes al poder notarial urgente, pero la pantalla de confirmacion les muestra: *"No se pudo procesar la solicitud. Error interno del servidor"*.
> 
> Tengo identificados al menos 14 casos identicos ocurridos entre las 08:30 y las 09:10 AM. Otro caso critico es el de la senora Maria Gonzalez (ticket #4418, documento `DOC-2024-8849`), quien necesita el poder especial para un tramite bancario antes de las 13:00.

### [09:16 CLT] Lider de Operaciones Legales:
> Cual es el impacto total de contratos y escrituras detenidos hoy? En el panel de control veo 14 documentos en estado "Error" o "Fallido", pero lo grave es que a todos esos clientes ya se les debito el dinero.
> 
> Si no destrabamos esto durante la manana, esos 14 clientes perderan sus citas notariales y tendremos que asumir costos de indemnizacion y anulacion de tramites. Ademas, legalmente no podemos dejar transacciones cobradas con escrituras no emitidas.
> 
> Podemos darles alguna estimacion o tiempo estimado de solucion? Necesito darles una respuesta clara y tranquilizadora a los clientes sin entrar en explicaciones tecnicas que los confundan.

### [09:21 CLT] Equipo de Ingenieria:
> Recibido el reporte. Estamos levantando el incidente INC-4092 con prioridad maxima e investigando el comportamiento anomalo del servicio para destrabar a los clientes urgentes. Les informaremos apenas tengamos novedades.

### [09:28 CLT] Lider de Operaciones Legales:
> Por favor mantengannos al tanto minuto a minuto. El equipo legal estara disponible para validar cualquier documento o formato que requiera revision antes de enviarlo a notaria. Lo prioritario es que los documentos de esos 14 clientes puedan emitirse correctamente para que alcancen a firmar hoy.

---

## 3. Lista de Casos Prioritarios Reportados

| ID Documento | ID Pago Flow | Cliente | Tramite Solicitado | Urgencia Notarial |
| :--- | :--- | :--- | :--- | :--- |
| `DOC-2024-8841` | `tx_pay_902148` | Juan Morales S. | Poder Especial Notarial | Notaria Providencia (14:00 hrs) |
| `DOC-2024-8849` | `tx_pay_902155` | Maria Gonzalez T. | Poder Especial Bancario | Notaria Santiago Centro (13:00 hrs) |
| `DOC-2024-8853` | `tx_pay_902162` | Carlos Henriquez P. | Poder Especial Automotriz | Notaria Las Condes (15:30 hrs) |
| `DOC-2024-8858` | `tx_pay_902170` | Patricia Fuenzalida | Poder Especial Judicial | Notaria Providencia (16:00 hrs) |

---

## 4. Proximos Pasos Operativos

1. Identificar el motivo de las respuestas 500 en las solicitudes de los clientes afectados.
2. Restablecer la emision de documentos para entregar los poderes a las personas que esperan en notaria.
3. Informar al equipo de Operaciones Legales una vez que los documentos pendientes puedan descargarse.
