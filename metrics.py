
from prometheus_client import Counter, Histogram, Gauge

events_processed = Counter(
    'stark_sensor_events_total',
    'Total de eventos de sensores procesados'
)

processing_latency = Histogram(
    'stark_processing_latency_seconds',
    'Latencia de procesamiento de eventos de sensor',
    buckets=(.005, .01, .025, .05, .075, .1, .25, .5, 1.0, 2.5, 5.0, 10.0, float('inf'))
)

request_counter = Gauge(
    'stark_http_requests_in_progress',
    'Solicitudes HTTP actualmente activas en el sistema de seguridad',
)
