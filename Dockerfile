FROM your-registry.example.com/tiangolo/meinheld-gunicorn-flask:python3.8-alpine3.11
RUN adduser -D -H -u 1001 todoist-adder
COPY  /app
RUN pip3 install -r /app/requirements.txt
USER todoist-adder
