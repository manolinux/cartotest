from models import *
from settings import Settings
from typing import Optional, List, Type, Any
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime 
from memoization import cached
from shapely import wkb
from shapely.geometry import mapping, shape
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

import json
import pydantic 
import requests
import logging


#Launch API
app = FastAPI(debug=True)


##################### SOME UTILITY FUNCTIONS ##########################


"""
Get stations info from Carto API
"""
@cached
def getStations():
    try:
        #Get all stations
        r = requests.get(Settings.stationsUrl.format('*')) 
        #We set the cache if status is 200
        if r.status_code == 200:
            stations = Stations.parse_raw(r.text)
            return stations
        else:
            return Stations(rows=list())

    except Exception as e:
            return Stations(rows=list())
    

"""
Obtain ordered dict from Stations, easier to index
"""
def getStationsDict(stations: Stations):
    return {x.station_id: x for x in stations.rows}

"""
Filter stations by ids, and/or geom
Could by achieved too by using database, but we're use shapely for vector intersections
"""

@cached
def filterStations(stationIds: List[str] = list(), geom = None):
    
    filteredStations = []
    allStations = getStations()
    
    #Filter by ids?
    if len(stationIds) > 0:
        for station_id in stationIds:
            filteredStations = list(filter(lambda x: x.station_id == station_id ,allStations.rows))
    else:
        filteredStations = allStations
    
    #Filter by geom
    if geom is not None:
        polygon = shape(json.loads(geom))
        geomFilteredStations = Stations(rows=list(filter(lambda x: 
                    wkb.loads(x.the_geom, hex=True).intersects(polygon),filteredStations.rows)))
    else:
        geomFilteredStations = filteredStations
                            
    return geomFilteredStations

"""
Sets population in every station
"""
def setStationsPopulation(stations: Stations):
    for station in stations.rows:
        station.population = getStationPopulation(station.station_id,station.the_geom)

"""
Cached population of station
Two args, instead of Station object for caching, maybe if we
pass full object caching is not working
"""

@cached
def getStationPopulation(station_id: str, hexWkt: str):
    try:
        #Get station by params
        r = requests.get(Settings.stationsUrlPopulation.format(station_id,hexWkt))
        #We set the cache if status is 200
        if r.status_code == 200:        
            return StationsPopulation.parse_raw(r.text).rows[0].population
        else:
            return Settings.notAvailablePopulation

    except Exception as e:
            return Settings.notAvailablePopulation
   
        

##################### APPLICATION EVENTS #####################
"""
Initialization
"""
@AuthJWT.load_config
def getAuthConfig():
    return Settings.authSettings

@AuthJWT.token_in_denylist_loader
def checkIfTokenInDenyList(decrypted_token):
    jti = decrypted_token['jti']
    return jti in app.denyTokenList

@app.on_event('startup')
def startup():

    #Get logger
    logger = logging.getLogger(__name__)

    #First cached-load of stations, should be few
    #It could have a ttl, too
    #But now we're not worrying about refreshing stations
    app.allStations = getStations()

    #Cache population too
    for station in app.allStations.rows:
        getStationPopulation(station.station_id,station.the_geom)

    #Valid tokens list
    app.denyTokenList = []


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    ) 

@app.post('/login')
def login(user: User, Authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401,detail="Bad username or password")

    # Create the tokens and passing to set_access_cookies or set_refresh_cookies
    access_token = Authorize.create_access_token(subject=user.username)
   
    return {"msg":"Successfully logged in",
            "access_token" : access_token}


@app.get('/logout')
def logout(Authorize: AuthJWT = Depends()):
    """
    Mark token as unusable
    """
    jti = Authorize.get_raw_jwt()['jti']
    app.denyTokenList.append(jti)
    return {"msg":"Successfully logged out"}

##################### API ENDPOINTS ##########################

"""
Example:
/stations/measure/max/co/0200101/20210101?stations=sta1,sta2&geom=POINT(1 2)
"""
@app.get("/stations/measure/{function}/{variable}/{fromDate}/{toDate}")
def getMeasure(function: str, variable: str,
                fromDate: str, toDate: str, 
                stations: Optional[List[str]] = list(),
                geom: Optional[str] = None,
                Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_required()
    
    #Get stations, and set population
    stationsList = getStations()
    setStationsPopulation(stationsList)
    
    #Get only those stations which meet the geom & id filter
    stationsDict = getStationsDict(filterStations(stations,geom))

    #If had an error recovering stations, we cannot give stats
    #better invalidate cache and give another try
    if len(stationsDict) == 0:
        getStations.cache_clear()
        return ResultsMeasureEp(rows=list())
    else:
        fromDateTs = datetime.strptime(fromDate,'%Y%m%d')
        toDateTs = datetime.strptime(toDate,'%Y%m%d')
        
        #Build query
        observationsFullQuery = (Settings.observationsStatsUrl + 
            " where timeinstant >= '{2}' and timeinstant <= '{3}' group by station_id").format(
                function,variable,fromDateTs,toDateTs)   
        
        #Request it
        try:
            r = requests.get(observationsFullQuery)
            #We set the cache if status is 200
            if r.status_code == 200: 
                #We get the observations
                observations =  ResultsMeasureEp.parse_raw(r.text)
                
                #Remove observations not linked to stationsID array
                #nor to geom filter

                #Observations are all and filteredObservations are those which
                #meet the query param criteria
                filteredObservations = ResultsMeasureEp(rows=list())
                for observation in observations.rows:
                    try:
                        observation.population = stationsDict[observation.station_id].population
                        filteredObservations.rows.append(observation)
                    #Key not found
                    except Exception as e:
                        pass

                return filteredObservations
            else:
                return ResultsMeasureEp(rows=list())

        except Exception as e:
            return ResultsMeasureEp(rows=list())


"""
Example:
/stations/timeseries/max/co/hour/0200101/20210101?stations=sta1,sta2&geom=POINT(1 2)
"""
@app.get("/stations/timeseries/{function}/{variable}/{tsStep}/{fromDate}/{toDate}")
def getMeasureTimeseries(function: str, variable: str,
                tsStep: str, fromDate: str, toDate: str, 
                stations: Optional[List[str]] = list(),
                geom: Optional[str] = None,
                Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_required()

    #Get stations, and set population
    stationsList = getStations()
    setStationsPopulation(stationsList)
    
    #Get only those stations which meet the geom & id filter
    stationsDict = getStationsDict(filterStations(stations,geom))
    
    if len(stationsDict) == 0:
        getStations.cache_clear()
        return ResultsTimeSeriesEp(rows=[])
    else:
        #Lets build full query

        fromDateTs = datetime.strptime(fromDate,'%Y%m%d')
        toDateTs = datetime.strptime(toDate,'%Y%m%d')
        
        #Build query
        observationsFullQuery = (Settings.observationsTSeriesUrl + 
            " where timeinstant >= '{3}' and timeinstant <= '{4}' group by station_id, timeinstant order by occurred_at asc").format(
                    function,variable,tsStep,fromDateTs,toDateTs)   
        
        #Request it
        try:
            r = requests.get(observationsFullQuery)
            #We set the cache if status is 200
            if r.status_code == 200:
                #We get the observations
                observations =  ResultsTimeSeriesEp.parse_raw(r.text)


                #Remove observations not linked to stationsID array
                #nor to geom filter

                #Observations are all and filteredObservations are those which
                #meet the query param criteria
                filteredObservations = ResultsTimeSeriesEp(rows=list())
                for observation in observations.rows:
                    try:
                        observation.population = stationsDict[observation.station_id].population
                        filteredObservations.rows.append(observation)
                    #Key not found
                    except Exception as e:
                        pass
                return filteredObservations
            else:
                return ResultsTimeSeriesEp(rows=list())

        except Exception as e:
            return ResultsTimeSeriesEp(rows=list())

"""
    Bonus: stations to print in a map
"""
@app.get("/stations")
def stationsEndpoint(Authorize: AuthJWT = Depends()):
    
    Authorize.jwt_required()

    #Get stations, and set population
    stationsList = getStations()
    setStationsPopulation(stationsList)
    
    return stationsList