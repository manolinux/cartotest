FROM python:3.8-slim-buster
RUN apt-get update && apt-get install -y bash bash-builtins
RUN apt-get install supervisor -y
ENV STREAMLIT_SERVER_PORT=8001
WORKDIR /app
RUN python3 -m venv .
RUN mkdir /app/log
COPY requirements.txt /app/
COPY start.sh /app/
COPY supervisor.conf /app/
RUN . bin/activate && pip3 install -r /app/requirements.txt
COPY *.py /app/
COPY supervisor.conf /app/
ENTRYPOINT ["/app/start.sh"]
EXPOSE 8000
EXPOSE 8001
