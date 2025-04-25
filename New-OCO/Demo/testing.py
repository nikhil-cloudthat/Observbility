import os
import time
import random
import logging
from flask import Flask, Response, request
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
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
from opentelemetry.trace import Status, StatusCode

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

# Create OpenTelemetry metrics
request_counter = meter.create_counter(
    name="http_requests",
    description="Total number of HTTP requests",
    unit="1",
)
latency_histogram = meter.create_histogram(
    name="http_request_duration",
    description="HTTP request latency",
    unit="s",
)
error_counter = meter.create_counter(
    name="request_errors",
    description="Number of request errors",
    unit="1",
)
db_query_latency = meter.create_histogram(
    name="db_query_latency",
    description="Database query latency in seconds",
    unit="s",
)
cache_hit_counter = meter.create_counter(
    name="cache_hits",
    description="Number of cache hits",
    unit="1",
)
cache_miss_counter = meter.create_counter(
    name="cache_misses",
    description="Number of cache misses",
    unit="1",
)
api_call_latency = meter.create_histogram(
    name="api_call_latency",
    description="External API call latency in seconds",
    unit="s",
)
business_logic_counter = meter.create_counter(
    name="business_logic_operations",
    description="Number of business logic operations performed",
    unit="1",
)

# Prometheus metrics
prometheus_request_counter = Counter(
    'http_requests_total', 'Total number of HTTP requests', ['method', 'path', 'status_code']
)
prometheus_request_latency = Histogram(
    'http_request_duration_seconds', 'HTTP request latency', ['method', 'path', 'status_code']
)
prometheus_error_counter = Counter(
    'request_errors_total', 'Total number of request errors'
)
prometheus_db_query_latency = Histogram(
    'db_query_latency_seconds', 'Database query latency in seconds'
)
prometheus_cache_hit_counter = Counter(
    'cache_hits_total', 'Total number of cache hits'
)
prometheus_cache_miss_counter = Counter(
    'cache_misses_total', 'Total number of cache misses'
)
prometheus_api_call_latency = Histogram(
    'api_call_latency_seconds', 'External API call latency in seconds'
)
prometheus_business_logic_counter = Counter(
    'business_logic_operations_total', 'Total number of business logic operations'
)

# Main application logic
def process_request():
    with tracer.start_as_current_span("process_request") as request_span:
        method = request.method
        path = request.path
        request_span.set_attribute("http.method", method)
        request_span.set_attribute("http.target", path)
        try:
            with tracer.start_as_current_span("handle_request") as handle_span:
                with tracer.start_as_current_span("pre_process") as pre_span:
                    with tracer.start_as_current_span("receive_request") as receive_span:
                        time.sleep(random.uniform(0.01, 0.05))
                    with tracer.start_as_current_span("parse_request") as parse_span:
                        time.sleep(random.uniform(0.01, 0.05))
                    with tracer.start_as_current_span("validate_input") as validate_span:
                        if random.random() < 0.1:
                            validate_span.set_status(Status(StatusCode.ERROR, description="Invalid input"))
                            raise ValueError("Invalid input")
                with tracer.start_as_current_span("process") as process_span:
                    with tracer.start_as_current_span("authenticate_user") as auth_span:
                        if random.random() < 0.05:
                            auth_span.set_status(Status(StatusCode.ERROR, description="Authentication failed"))
                            raise Exception("Authentication failed")
                    with tracer.start_as_current_span("check_cache") as cache_span:
                        if random.random() < 0.7:
                            cache_hit_counter.add(1)
                            prometheus_cache_hit_counter.inc()
                        else:
                            cache_miss_counter.add(1)
                            prometheus_cache_miss_counter.inc()
                    with tracer.start_as_current_span("fetch_data") as fetch_span:
                        fetch_start = time.time()
                        time.sleep(random.uniform(0.05, 0.2))
                        fetch_end = time.time()
                        db_latency = fetch_end - fetch_start
                        db_query_latency.record(db_latency)
                        prometheus_db_query_latency.observe(db_latency)
                    with tracer.start_as_current_span("call_external_api") as api_span:
                        api_start = time.time()
                        time.sleep(random.uniform(0.1, 0.3))
                        api_end = time.time()
                        api_latency = api_end - api_start
                        api_call_latency.record(api_latency)
                        prometheus_api_call_latency.observe(api_latency)
                    with tracer.start_as_current_span("process_data") as process_data_span:
                        time.sleep(random.uniform(0.1, 0.3))
                        business_logic_counter.add(1)
                        prometheus_business_logic_counter.inc()
                with tracer.start_as_current_span("post_process") as post_span:
                    with tracer.start_as_current_span("generate_response") as generate_span:
                        time.sleep(random.uniform(0.01, 0.05))
                    with tracer.start_as_current_span("send_response") as send_span:
                        time.sleep(random.uniform(0.01, 0.05))
                    with tracer.start_as_current_span("log_request") as log_span:
                        logger.info("Request processed successfully")
            request_span.set_attribute("http.status_code", 200)
            return "Request processed", 200
        except Exception as e:
            request_span.set_status(Status(StatusCode.ERROR, description=str(e)))
            request_span.set_attribute("http.status_code", 500)
            error_counter.add(1)
            prometheus_error_counter.inc()
            logger.error(f"Error processing request: {str(e)}")
            return "Error processing request", 500

def handle_request(process_func):
    start_time = time.time()
    response, status = process_func()
    end_time = time.time()
    latency = end_time - start_time
    method = request.method
    path = request.path
    attributes = {"method": method, "path": path, "status_code": str(status)}
    request_counter.add(1, attributes=attributes)
    latency_histogram.record(latency, attributes=attributes)
    prometheus_request_counter.labels(method=method, path=path, status_code=str(status)).inc()
    prometheus_request_latency.labels(method=method, path=path, status_code=str(status)).observe(latency)
    return response, status

# Define Flask routes
@app.route('/')
def index():
    return handle_request(process_request)

@app.route('/api/data')
def api_data():
    return handle_request(process_request)

# Define /metrics route to expose Prometheus metrics
@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics."""
    data = generate_latest()  # Generate latest metrics data
    return Response(data, mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Start the Flask web server