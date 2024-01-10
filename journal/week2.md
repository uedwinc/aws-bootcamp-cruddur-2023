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


## X-Ray

### Instrument AWS X-Ray for Flask

- Add your AWS region as environment variable

```sh
export AWS_REGION="us-east-2"
gp env AWS_REGION="us-east-2"
```

- Add to the `requirements.txt`

```py
aws-xray-sdk
```

- Install python dependencies

```sh
pip install -r requirements.txt
```

- Add to `app.py`

```py
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

xray_url = os.getenv("AWS_XRAY_URL")
xray_recorder.configure(service='backend-flask', dynamic_naming=xray_url)
XRayMiddleware(app, xray_recorder)
```

### Setup AWS X-Ray Resources

- Add `aws/json/xray.json` to setup sampling rule

```json
{
  "SamplingRule": {
      "RuleName": "Cruddur",
      "ResourceARN": "*",
      "Priority": 9000,
      "FixedRate": 0.1,
      "ReservoirSize": 5,
      "ServiceName": "backend-flask",
      "ServiceType": "*",
      "Host": "*",
      "HTTPMethod": "*",
      "URLPath": "*",
      "Version": 1
  }
}
```

- Create an x-ray group

```sh
aws xray create-group \
   --group-name "Cruddur" \
   --filter-expression "service(\"backend-flask\")"
```

- Run sampling rule

```sh
aws xray create-sampling-rule --cli-input-json file://aws/json/xray.json
```

### Installing X-Ray Daemon

**Docs:**

- [Install X-ray Daemon](https://docs.aws.amazon.com/xray/latest/devguide/xray-daemon.html)

    - This is to install locally:

    ```sh
    wget https://s3.us-east-2.amazonaws.com/aws-xray-assets.us-east-2/xray-daemon/aws-xray-daemon-3.x.deb
    sudo dpkg -i **.deb
    ```

- [Github aws-xray-daemon](https://github.com/aws/aws-xray-daemon)

- [X-Ray Docker Compose example](https://github.com/marjamis/xray/blob/master/docker-compose.yml)


**Add Deamon Service to Docker Compose**

```yml
  xray-daemon:
    image: "amazon/aws-xray-daemon"
    environment:
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
      AWS_REGION: "us-east-1"
    command:
      - "xray -o -b xray-daemon:2000"
    ports:
      - 2000:2000/udp
```

- We need to add these two env vars to our backend-flask in our `docker-compose.yml` file

```yml
      AWS_XRAY_URL: "*4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}*"
      AWS_XRAY_DAEMON_ADDRESS: "xray-daemon:2000"
```

- Now, do `docker compose up`