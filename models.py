from pydantic import BaseModel
from datetime import datetime 
from typing import Optional, List, Type, Any, Dict


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
    variable: str
    station_id: str
    function: str
    value: float
    population: Optional[float]

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
    variable: str
    station_id: str
    function: str
    value: float
    population: Optional[float]
    occurred_at: Optional[datetime]

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
    cartodb_id: int
    the_geom: str
    the_geom_webmercator: str
    station_id: str
    created_at: datetime
    updated_at: datetime
    population: Optional[float]

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
    