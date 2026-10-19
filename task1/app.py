import random
import time

from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

resource = Resource.create({"service.name": "flask-otel-demo"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def index():
    return "Hello from Flask + OpenTelemetry + Jaeger!\n"

@app.route("/rolldice")
def roll_dice():
    with tracer.start_as_current_span("roll-dice") as span:
        result = random.randint(1, 6)
        span.set_attribute("dice.value", result)
        time.sleep(0.05)
        return f"Rolled: {result}\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
