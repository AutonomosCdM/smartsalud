💰 Análisis de Costos - Twilio WhatsApp para Chile
📊 Estructura de Precios (2025)
Costo Total = Fee de Twilio + Fee de Meta
1️⃣ Fee de Twilio (Fija)
$0.005 USD por mensaje (inbound + outbound)
Aplica a TODOS los mensajes
2️⃣ Fee de Meta (Variable por Tipo)
Chile (CL):
✅ Utility Template: $0.004 USD/mensaje (GRATIS durante ventana de 24h)
🔐 Authentication Template: $0.004 USD/mensaje (siempre cobra)
📣 Marketing Template: $0.000 USD (GRATIS)
💬 Free-form Messages: $0.000 USD (solo durante ventana de 24h)
🔄 Ventana de Servicio al Cliente (24 horas)
Cuando un usuario te escribe, se abre una ventana de 24 horas donde:
✅ Utility templates son GRATIS (solo pagas Twilio $0.005)
✅ Mensajes de texto libre son GRATIS (solo pagas Twilio $0.005)
⏱️ La ventana se reinicia cada vez que el usuario te escribe
💵 Cálculo de Costos para smartSalud
Escenario 1: Usuario Confirma Cita ✅
Mensaje	Tipo	Twilio Fee	Meta Fee	Total
1. Recordatorio inicial con botones	Utility Template	$0.005	$0.004	$0.009
2. Usuario presiona "Confirmar" (inbound)	-	$0.005	$0.000	$0.005
3. Respuesta "Cita confirmada"	Free-form (dentro 24h)	$0.005	$0.000	$0.005
TOTAL POR CONFIRMACIÓN				$0.019 USD
~$20 CLP por confirmación (usando tasa ~1050 CLP/USD)
Escenario 2: Usuario Cancela y Reagenda ❌➡️📅
Mensaje	Tipo	Twilio Fee	Meta Fee	Total
1. Recordatorio inicial con botones	Utility Template	$0.005	$0.004	$0.009
2. Usuario presiona "Cancelar" (inbound)	-	$0.005	$0.000	$0.005
3. Prompt "¿Deseas reagendar?" con botones	Free-form (dentro 24h)	$0.005	$0.000	$0.005
4. Usuario presiona "Sí, reagendar" (inbound)	-	$0.005	$0.000	$0.005
5. Opciones de timeslot con botones	Free-form (dentro 24h)	$0.005	$0.000	$0.005
6. Usuario selecciona horario (inbound)	-	$0.005	$0.000	$0.005
7. Confirmación nueva cita	Free-form (dentro 24h)	$0.005	$0.000	$0.005
TOTAL POR CANCELACIÓN + REAGENDAMIENTO				$0.039 USD
~$41 CLP por flujo completo (usando tasa ~1050 CLP/USD)
Escenario 3: Usuario Cancela Sin Reagendar ❌
Mensaje	Tipo	Twilio Fee	Meta Fee	Total
1. Recordatorio inicial con botones	Utility Template	$0.005	$0.004	$0.009
2. Usuario presiona "Cancelar" (inbound)	-	$0.005	$0.000	$0.005
3. Prompt "¿Deseas reagendar?" con botones	Free-form (dentro 24h)	$0.005	$0.000	$0.005
4. Usuario presiona "No, gracias" (inbound)	-	$0.005	$0.000	$0.005
5. Mensaje despedida	Free-form (dentro 24h)	$0.005	$0.000	$0.005
TOTAL POR CANCELACIÓN				$0.029 USD
~$30 CLP por cancelación
📈 Proyección Mensual para CESFAM Futrono
Asumiendo 100 citas por mes:
Escenario	% Estimado	Cantidad	Costo Unitario	Costo Total
Confirman	70%	70 citas	$0.019	$1.33 USD
Cancelan + Reagendan	20%	20 citas	$0.039	$0.78 USD
Cancelan sin reagendar	10%	10 citas	$0.029	$0.29 USD
TOTAL MENSUAL		100 citas		$2.40 USD
💰 Costo Total Estimado: ~$2,500 CLP/mes (100 citas)
🎯 Optimizaciones para Reducir Costos
✅ Estrategias Implementadas en tu Sistema:
Aprovechar ventana de 24h ✅
Todos los mensajes después del inicial son free-form
Solo pagas $0.005 de Twilio (no Meta fee)
Ahorro: ~40%
Botones interactivos ✅
Mensajes inbound del usuario no tienen Meta fee
Solo pagas $0.005 de Twilio
Reduce mensajes de texto libre
Templates de tipo Utility ✅
Más baratos que Authentication ($0.004 vs $0.004)
GRATIS durante ventana de 24h
Ideales para recordatorios de citas
💡 Recomendaciones Adicionales:
Enviar recordatorios 48h antes
Maximiza uso de ventana de 24h
Usuario probablemente responde el mismo día
Consolidar mensajes
Un mensaje con toda la info en vez de múltiples
Menos mensajes = menos costo
Usar Marketing templates para promociones
Meta fee = $0.000 (GRATIS)
Solo pagas Twilio $0.005
📊 Comparación con Alternativas
Opción	Costo por interacción	Notas
WhatsApp (tu sistema)	$0.019 - $0.039	Automatizado, 24/7
Llamada telefónica	~$0.10 - $0.50	Requiere personal
SMS tradicional	$0.01 - $0.03	Sin botones interactivos
Email	~$0.001	Baja tasa de apertura
WhatsApp ofrece el mejor balance costo/efectividad para recordatorios médicos ✅
🚀 Conclusión
Tu sistema es MUY económico:
~$2.40 USD/mes para 100 citas
~$20-41 CLP por interacción completa
ROI positivo: evita llamadas telefónicas y no-shows