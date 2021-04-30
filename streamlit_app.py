from pydantic.errors import DataclassTypeError
import streamlit as st
from streamlit_folium import folium_static
from settings import Settings
from datetime import datetime,date
import requests
import folium
import pandas as pd
import json
from shapely import wkb

st.title("CartoDB interview test")
today = date.today()

variable = st.sidebar.selectbox("Seleccione variable:", Settings.variables)
funcion = st.sidebar.selectbox("Seleccione función agregadora:",Settings.functions)

dateFrom = st.sidebar.date_input('Fecha inicio:',today)
dateTo = st.sidebar.date_input('Fecha final:', today)

if dateTo < dateFrom:
    st.error('Error: La fecha de inicio debe ser mayor que la de final')

geom = st.sidebar.text_input("Filtro intersección", Settings.intersectionFilter)
ids = st.sidebar.text_input("Filtro estaciones", ",".join(Settings.stationsFilter))
ep1 = st.sidebar.button("Observaciones(tablas)")
step = st.sidebar.selectbox("Paso para series:", Settings.seriesStep)
ep2 = st.sidebar.button("Observaciones(series)")
ep3 = st.sidebar.button("?")
#Pulsado botón para el endpoint 1
if ep1:
    #login
    r = requests.post(Settings.loginUrl, json = {"username": "test", "password" : "test"})
    if (r.status_code == 200):
        st.success("Login ok")
        token = r.json()["access_token"]
        headers = {"Authorization": "Bearer " + token}

        obsUrl = Settings.endpoint1 + "/" + funcion + "/" + variable + "/" + \
             dateFrom.strftime("%Y%m%d") + "/" + dateTo.strftime("%Y%m%d")
        r = requests.get(obsUrl,params = {"stations" : ids, "geom" : geom}, headers=headers)

        if r.status_code == 200:
            st.success("Recuperadas observaciones")
            content = json.loads(r.text)
            df = pd.DataFrame(content["rows"])
            st.dataframe(df)
            st.balloons()

        else:
            st.error("Error observaciones, url:{0} status:{1}, error:{2}".format(obsUrl,r.status_code, r.text))
    else:
        st.error("Login nok, status:{0}, error:{1}".format(r.status_code, r.text))

elif ep2:
     #login
    r = requests.post(Settings.loginUrl, json = {"username": "test", "password" : "test"})
    if (r.status_code == 200):
        st.success("Login ok")
        token = r.json()["access_token"]
        headers = {"Authorization": "Bearer " + token}


        seriesUrl =  Settings.endpoint2 + "/" + funcion + "/" + variable + "/" + \
            step + "/" + dateFrom.strftime("%Y%m%d") + "/" + dateTo.strftime("%Y%m%d")
        r = requests.get(seriesUrl,params = {"stations" : ids, "geom" : geom},headers = headers)

        if r.status_code == 200:
            st.success("Recuperadas series")
            content = json.loads(r.text)
            df = pd.DataFrame(content["rows"])
            st.dataframe(df)
            st.balloons()
        else:
            st.error("Error series, url:{0}, status:{1}, error:{2}".format(seriesUrl,r.status_code, r.text))
    else:
        st.error("Login nok, status:{0}, error:{1}".format(r.status_code, r.text))

elif ep3:
        #login
        r = requests.post(Settings.loginUrl, json = {"username": "test", "password" : "test"})
        if (r.status_code == 200):
            st.success("Login ok")
            token = r.json()["access_token"]
            headers = {"Authorization": "Bearer " + token}

            r = requests.get(Settings.endpoint3,headers = headers)
            if r.status_code == 200:
                content = json.loads(r.text)
                st.success("Recuperadas estaciones")
                m = folium.Map(location=[40.4168,-3.7038], zoom_start=10)
                for station in content["rows"]:
                    point = wkb.loads(station["the_geom"], hex=True)
                    folium.Marker(
				        location=[point.y, point.x],
				        popup=station["station_id"]).add_to(m)
		
                # call to render Folium map in Streamlit
                folium_static(m)
                st.balloons()
    
            else:
                st.error("Error en estaciones, url:{0}, status:{1}, error:{2}".format(Settings.stationsUrl,r.status_code, r.text))
        else:
            st.error("Login nok, status:{0}, error:{1}".format(r.status_code, r.text))