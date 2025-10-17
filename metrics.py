# metrics.py

# Cambia la importación para incluir Gauge
from prometheus_client import Counter, Histogram, Gauge

# Contador de eventos de sensores recibidos
events_processed = Counter(
    'stark_sensor_events_total',
    'Total de eventos de sensores procesados'
)

# Histograma para medir la latencia
processing_latency = Histogram(
    'stark_processing_latency_seconds',
    'Latencia de procesamiento de eventos de sensor',
    buckets=(.005, .01, .025, .05, .075, .1, .25, .5, 1.0, 2.5, 5.0, 10.0, float('inf'))
)

# CAMBIAR ESTA SECCIÓN:
# Usa Gauge para rastrear las peticiones en curso, permitiendo el decorador .track_inprogress()
request_counter = Gauge( # <--- CAMBIO CLAVE: Ahora es un Gauge
    'stark_http_requests_in_progress', # <--- Renombrado para reflejar lo que hace
    'Solicitudes HTTP actualmente activas en el sistema de seguridad',
)
# ¡Nota! Hemos quitado la etiqueta ['endpoint'] ya que Gauge.track_inprogress() no la usa por defecto.