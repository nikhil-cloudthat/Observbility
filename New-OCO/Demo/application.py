import os
import time
import random
import logging
from flask import Flask, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter as PrometheusCounter
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# Initialize Flask app
app = Flask(__name__)

# Environment variables for endpoints
ALLOY_ENDPOINT = os.getenv('ALLOY_ENDPOINT', 'http://alloy:4323')

# Configure OpenTelemetry resource
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: "my-python-service"
})

# Configure OpenTelemetry tracing
trace.set_tracer_provider(TracerProvider(resource=resource))
otlp_span_exporter = OTLPSpanExporter(endpoint=ALLOY_ENDPOINT)
span_processor = BatchSpanProcessor(otlp_span_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Configure OpenTelemetry metrics with OTLP exporter
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=ALLOY_ENDPOINT)
)
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

# Configure OpenTelemetry logging
logger_provider = LoggerProvider(resource=resource)
otlp_log_exporter = OTLPLogExporter(endpoint=ALLOY_ENDPOINT)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

# Get logger and set handler
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# OpenTelemetry tracer and meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Create an OpenTelemetry counter metric
request_counter = meter.create_counter(
    name="request_counter",
    description="Counts the number of requests",
    unit="1",
)

# Prometheus counter for request tracking
prometheus_request_counter = PrometheusCounter(
    "prometheus_request_counter_total", "Counts the number of requests processed", ["trace_id"]
)

# Main application logic
def process_request():
    with tracer.start_as_current_span("process_request") as span:
        # Simulate some processing work
        time.sleep(random.uniform(0.1, 0.5))

         # Get the current trace ID to use as an exemplar in Prometheus
        trace_id = span.get_span_context().trace_id
        
        # Record OpenTelemetry metrics and Prometheus counter with an exemplar
        request_counter.add(1)
        
        # Add the trace_id as an exemplar
        prometheus_request_counter.labels(trace_id=hex(trace_id)[2:]).inc()  # Exemplar with trace_id

        # Log information
        logger.info("Request processed successfully")

        # Add an attribute to the span
        span.set_attribute("request.id", str(random.randint(1000, 9999)))


# Define Flask route for handling requests
@app.route('/')
def handle_request():
    process_request()  # Call your request processing logic here
    return "Request processed"

# Define /metrics route to expose Prometheus metrics
@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics."""
    data = generate_latest()  # Generate latest metrics data
    return Response(data, mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Start the Flask web server
