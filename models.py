from pydantic import BaseModel,validator
from datetime import datetime 
from typing import Optional, List, Type, Any, Dict
from settings import Settings
from shapely import wkb
import geojson
import enum
import re


"""
Validators set here to be reused across models
"""

#Function must be in list of functions
def valFunction(cls,function):
        if function in Settings.functions: return function
        else: raise ValueError("Function {0} not in {1}".format(function,str(Settings.functions)))

#Variable must be in list of variables
def valVariable(cls,variable):
        if variable in Settings.variables: return variable
        else: raise ValueError("Variable {0} not in {1}".format(variable,str(Settings.variables)))

#Geom must be a WKB hex geometry
#It should be checked too that the SRS is WGS84 for the_geom
#or Spherical Mercator for the_geom_web_merctor
def valWkbGeom(cls,geom):
    try:
        shapelyGeom = wkb.loads(geom,hex=True)
        return geom
    except Exception as e:
        raise ValueError("Value {0} is not a valid geom".format(str(geom)))

#Geom must be a GeoJSON geometry
def valGeoJSONGeom(cls,geom):
    try:
         if geom == None: return None
         geojson.loads(geom)
         return geom
    except Exception as e:
        raise ValueError("Geojson {0} is not a valid geom".format(str(geom)))

#Date must be in format YYYmmdd
def valDate(cls,date):
    try:
        dateStr = datetime.strptime(date,"%Y%m%d")
        return dateStr
    except Exception as e:
        raise ValueError("Date {0} is not a valid YYYYmmdd date".format(str(date)))


#Validate a comma separated list of strings
def valStrList(cls,values):
    try:
        if values.startswith(",") or values.endswith(","): raise ValueError
        return values    
    except Exception as e:
        raise ValueError("List {0} is not a valid comma-separated list of strings".format(values))

#Validate time-series step in settings values
def valTsStep(cls,step):
    try:
        if step in Settings.seriesStep: return step
    except Exception as e:
        raise ValueError("Step {0} is not a valid step for timeseries".format(step))

"""
Model for requesting observations of station
"""

class MeasureRequest(BaseModel):
    function: str
    variable: str
    fromDate: str 
    toDate: str
    stations: Optional[str]
    geom: Optional[str]
    _ensure_variable_in_values: classmethod = validator("variable", allow_reuse=True)(valVariable)
    _ensure_function_in_values: classmethod = validator("function", allow_reuse=True)(valFunction)
    _ensure_datefrom_format:  classmethod = validator("fromDate", allow_reuse=True)(valDate)
    _ensure_dateto_format:  classmethod = validator("toDate", allow_reuse=True)(valDate)
    _ensure_stations_list:  classmethod = validator("stations", allow_reuse=True)(valStrList)
    _ensure_geojson_geom: classmethod = validator("geom", allow_reuse=True)(valGeoJSONGeom)

"""
Model for requesting timeseries of stations
"""

class TimeSeriesRequest(BaseModel):
    function: str
    variable: str
    tsStep: str 
    fromDate: str 
    toDate: str 
    stations: Optional[str]
    geom: Optional[str]
    _ensure_variable_in_values: classmethod = validator("variable", allow_reuse=True)(valVariable)
    _ensure_function_in_values: classmethod = validator("function", allow_reuse=True)(valFunction)
    _ensure_datefrom_format:  classmethod = validator("fromDate", allow_reuse=True)(valDate)
    _ensure_dateto_format:  classmethod = validator("toDate", allow_reuse=True)(valDate)
    _ensure_stations_list:  classmethod = validator("stations", allow_reuse=True)(valStrList)
    _ensure_geojson_geom: classmethod = validator("geom", allow_reuse=True)(valGeoJSONGeom)
    _ensure_tsStep: classmethod = validator("tsStep", allow_reuse=True)(valTsStep)

"""
Model for single observation of station
"""
class Observation1(BaseModel):
    cartodb_id: int
    the_geom: Optional[str]
    the_geom_webmercator: Optional[str]
    station_id: str 
    timeinstant: datetime
    so2: float
    no2: float
    pm10: float
    pm2_5: float
    co: float 
    o3: float
    created_at: datetime
    updated_at: datetime

"""
 List of observations
"""
class Observations1(BaseModel):
    rows: List[Observation1]
    

"""
Model for single result of first endpoint /stations/measure
"""
class ResultMeasureEp(BaseModel):
    #fields
    variable: str
    station_id: str
    function: str
    value: float
    population: Optional[float]
    # validators
    _ensure_variable_in_values: classmethod = validator("variable", allow_reuse=True)(valVariable)
    _ensure_function_in_values: classmethod = validator("function", allow_reuse=True)(valFunction)
    
                

"""
Model for list results of first endpoint
"""
class ResultsMeasureEp(BaseModel):
    rows: List[ResultMeasureEp]
    #We don't need this fields coming from Carto's response
    fields: Optional[Any]
    time: Optional[float]
    total_rows: Optional[int]

"""
Model for result of second endpoint /stations/timeseries
"""

class ResultTimeSeriesEp(BaseModel):
    #fields
    variable: str
    station_id: str
    function: str
    value: float
    population: Optional[float]
    occurred_at: Optional[datetime]
     # validators
    _ensure_variable_in_values: classmethod = validator("variable", allow_reuse=True)(valVariable)
    _ensure_function_in_values: classmethod = validator("function", allow_reuse=True)(valFunction)
    

"""
Model for list of results of second endpoint /stations/timeseries
"""
class ResultsTimeSeriesEp(BaseModel):
    rows: List[ResultTimeSeriesEp]
    #We don't need this fields coming from Carto's response
    fields: Optional[Any]
    time: Optional[float]
    total_rows: Optional[int]

"""
Model for station recovered from carto database
"""
class Station(BaseModel):
    #fields
    cartodb_id: int
    the_geom: str
    the_geom_webmercator: str
    station_id: str
    created_at: datetime
    updated_at: datetime
    population: Optional[float]
     # validators
    _ensure_geometry_the_geom: classmethod = validator("the_geom", allow_reuse=True)(valWkbGeom)
    _ensure_geometry_the_geom_webmercator: classmethod = validator("the_geom_webmercator", allow_reuse=True)(valWkbGeom)

"""
Model for list of stations recovered from carto database
"""
class Stations(BaseModel):
    rows: List[Station]


"""
StationPopulation model
"""

class StationPopulation(BaseModel):
    population: float

"""
StationsPopulation model
"""
class StationsPopulation(BaseModel):
    rows: List [StationPopulation]



"""
Authentication User
"""
class User(BaseModel):
    username: str
    password: str



"""
Auth settings
"""

class AuthSettings(BaseModel):
    #Secret key for generating tokens
    authjwt_secret_key: str 
    #Deny list for tokens enabled
    authjwt_denylist_enabled: Optional[bool]
    #Deny list 
    authjwt_denylist_token_checks: Optional[set] 
    