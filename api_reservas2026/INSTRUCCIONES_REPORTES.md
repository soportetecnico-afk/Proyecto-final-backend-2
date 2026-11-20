# Configuración de reportes

El módulo permite filtrar por tipo de reporte, rango de fechas y estado de la reserva. Exporta la tabla a Excel (`.xlsx`), permite guardar una copia PDF desde la ventana de impresión y puede enviar el detalle como CSV adjunto por correo.

Para habilitar el envío, copia las variables SMTP de `.env.example` al `.env` local y completa los datos del proveedor de correo. No compartas ese archivo porque contiene credenciales. `SMTP_PORT` usa 587 por defecto y la API inicia TLS.

El frontend utiliza `VITE_API_BASE_URL` si está definida; cuando no lo está, intenta `http://127.0.0.1:8000`. Para abrir el tablero en otra máquina o en un teléfono, configura esta variable con la dirección LAN o dominio donde se encuentre la API.
