FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt
COPY *.py /app/
CMD ["uvicorn",
ENV STREAMLIT_SERVER_PORT=8001
CMD streamlit run streamlit_app & disown
CMD uvicorn --reload --port 8000 main:app
EXPOSE 8000
EXPOSE 8001
