# Distributed Tracing

## HoneyComb

- Login to honeycomb at ui.honeycomb.io

- Create a new environment for cruddur and copy the API key

- Set the API key as environment variable

```
export HONEYCOMB_API_KEY="enter-key-here"
gp env HONEYCOMB_API_KEY="enter-key-here"
```

- Set the service name as environment variable

```
export HONEYCOMB_SERVICE_NAME="backend-flask"
gp env HONEYCOMB_SERVICE_NAME="backend-flask"
```

- Add the following Env Vars to `backend-flask` in docker compose

```yml
OTEL_EXPORTER_OTLP_ENDPOINT: "https://api.honeycomb.io"
OTEL_EXPORTER_OTLP_HEADERS: "x-honeycomb-team=${HONEYCOMB_API_KEY}"
OTEL_SERVICE_NAME: "${HONEYCOMB_SERVICE_NAME}"
```

**Instrument OpenTelemetry for HoneyComb**

- Add the following to `requirements.txt`

```
opentelemetry-api 
opentelemetry-sdk 
opentelemetry-exporter-otlp-proto-http 
opentelemetry-instrumentation-flask 
opentelemetry-instrumentation-requests
```

- Install these dependencies:

```sh
pip install -r requirements.txt
```

- Add the following to the `app.py`

```py
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
```

```py
# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
```

```py
# Initialize automatic instrumentation with Flask
app = Flask(__name__) #Skip this line as it is already in app.py
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
```

- Find the instructions for instrumentation here: https://docs.honeycomb.io/getting-data-in/opentelemetry/python-distro/ (This is a newer method slighly different from the one we used)

- Do `docker compose up` 
- Access the address and ports and check for tracing on honeycomb

- Follow instructions here to create spans for honeycomb: https://docs.honeycomb.io/getting-data-in/opentelemetry/python-distro/#creating-spans

- You can also add attributes to the span following documentation here: https://docs.honeycomb.io/getting-data-in/opentelemetry/python-distro/#adding-attributes-to-spans

