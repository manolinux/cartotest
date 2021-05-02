FROM python:3.8-slim-buster
RUN apt-get update && apt-get install -y bash bash-builtins
RUN apt-get install supervisor -y
ENV STREAMLIT_SERVER_PORT=8001
WORKDIR /app
CMD virtualenv .
CMD source bin/activate
CMD mkdir /app/log
COPY requirements.txt /app/
COPY supervisor.conf /app/
RUN pip3 install -r /app/requirements.txt
COPY *.py /app/
COPY supervisor.conf /app/
ENTRYPOINT ["/usr/bin/supervisord", "-n","-c","/app/supervisor.conf"]
EXPOSE 8000
EXPOSE 8001
