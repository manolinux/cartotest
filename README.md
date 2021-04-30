CARTODB TECHNICAL INTERVIEW TEST

GENERAL EXPLANATIONS

* Tried to do as much as possible when initalizing the server. Thought, as stations seemed to be not many, they could be cached (memoized) for later access; same applies to populations from stations, a spatial intersection of every station location and grid population data is performed initially and then cached for later use.

Endpoint1/ First endpoint, is in the form of following GET request:
/stations/measure/<function>/<variable>/YYYYmmdd/YYYYmmdd?stations=id1,id2,...&geom=WKT

As an example:
/stations/measure/max/co/20010101/20210101?stations=sta1,sta2&geom=POINT(-6.33 38.8)

Geoms are considered to be represented in WGS84 lonlat format, aka EPSG:4326

Expected fixed arguments, functions (max, min, avg), variables (co,so2,etc.), date range, have been set up as path parameters. Optional ones, filters for station ids and geometry for intersection are passed in as query arguments.
Possibly, a POST request could have been more appropiate, as the arguments may grow long and break url's limits.

So, after receiving arguments, checking and dealing with authentication, the pseudocode for first endpoint is:

        * Get stations (cached)
        * Set population in stations (cached)
        * Limit stations to those respecting filtes
            - id in list of ids
            - spatial intersection of stations geometries with given one, with shapely
        * Construct the url for Carto API, taking into accoun  function,variable,fromDateTs,toDateTs
        * Remove observations not linked to stationsId array (optional)
        * Nor to geom filter (optional)
        * Final observations go to filteredObservations 
        * Returned object with rows=empty in case of not being able to carry on all the process        

Endpoint2/ Second endpoint, is in the form of following GET request:
/stations/timeseries/<function>/<variable>/<step>/YYYYmmdd/YYYYmmdd?stations=id1,id2,...&geom=WKT

As an example:
/stations/timeseries/max/co/hour/20010101/20210101?stations=sta1,sta2&geom=POINT(-6.33 38.8)

Geoms are considered to be represented in WGS84 lonlat format, aka EPSG:4326

Expected fixed arguments, functions (max, min, avg), variables (co,so2,etc.), date range, have been set up as path parameters. Optional ones, filters for station ids and geometry for intersection are passed in as query arguments.
Possibly, a POST request could have been more appropiate, as the arguments may grow long and break url's limits.

So, after receiving arguments, checking and dealing with authentication, the pseudocode for first endpoint is:

        * Get stations (cached)
        * Set population in stations (cached)
        * Limit stations to those respecting filtes
            - id in list of ids
            - spatial intersection of stations geometries with given one, with shapely
        * Construct the url for Carto API, taking into accoun  function,variable,fromDateTs,toDateTs
          The key here is using DATE_TRUNC() function of Postgresql using step (hour, day, year) for being able to aggregate observations, grouping by station_id, timeinstant order
        * Remove observations not linked to stationsId array (optional)
        * Nor to geom filter (optional)
        * Final observations go to filteredObservations 
        * Returned object with rows=empty in case of not being able to carry on all the process      

Endpoint 3/ Was not required in the exercise. It is a GET request

/stations

that returns all the (cached) stations, in case we do something useful with them.

CHECKLIST

- Statistical measurement for stations (endpoint 1). DONE 
- Timeseries for stations(endpoint 2). DONE
- Filters. DONE (for ep1 and ep2)
- Authentication. DONE

ABOUT AUTHENTICATION

Although not required to implement authentication, FastAPI endpoints have been protected using a simple JWT Authentication Bearer schema.
Logout is implemented including token in a denylist; as it is not permanent by the moment, a server reload would imply that a denied token could be used again. Lists of tokens/users should be stored permanently in a database system. Redis could be a good alternative too. This simple system has not a mechanism of refreshing tokens, either, an expired token would force to ask the API for a new one. FastAPI JWT extension can deal with refresh tokens, and store them in cookies. The current way is via Authentication Bearer header in HTTP.

User for this demo API is:  test / test

The API should be protected with HTTPS too. No interchange of sensitive information should be carried out without encrypted support.
Uvicorn (the web server in which FastAPI is executed) has easy support for HTTPS. Certificate could be obtained via Let's Encrypt / Certbot, for instance

BONUS: DEPLOY

Deployment can be done in a Docker container, building it from scratch with the offered Dockerfile.
Image exposes two ports, 8000 for API, and 8001 for Streamlit.

BONUS: STREAMLIT

A minimal Streamlit application has been made for the sake of curiosity, and to be able to visualize easily results.
Tests can also be performed via the excellent ThunderClient replacement for Postman inside Visual Studio Code.

TESTING
Unit tests, using for instance, Python unittest, have to be implemented.

TECHNOLOGIES USED
* Python 3.8, virtualenv or conda for environment separation
* Uvicorn as web server, and FastAPI for (just knew Flask, and I wanted)
* Pydantic, very nice for modelling requests and responses when working with APIs
* Carto API for data 
* Shapely for vector data, intersections, crossings and so on
* Visual Studio Code, the best IDE I know (at least for Python)
* Thunder Client plugin for Visual Studio Code, as a replacement for Postman, great to check APIs
* Streamlit for visualization. I really love Streamlit, it's possibilities are endless!
* Docker for containerization and distribution
* Fedora Core 31, as I'm more redhatish than debianer (worked some years administering Scientific Linux machines)
* Headphones for isolating myself from my little's piano apprentice: Marco, please, don't use the pedals!!!!

TO BE DONE

* Go HTTPS, uvicorn and fastapi have no problems with https (Certbot and Let's encrypt for certificates, for example)
* Improve checks for models 
* Improve error handling (there is very little there)
* Improve caching of stations and station population, apply time to live (ttl) 
* Station population is related to station with two queries, as I really don't know for the moment how to perform joins in Carto.
* Improve authentication. The JWT Token Bearer authentication is very simple, tokens are in denylist in memory, when server reboots denylist is lost, which allows an invalid token to enter the app. Could implement another scheme, like OAuth2, etc, or improve JWT with refresh tokens support and session backend storage and retrieval (database, Redis).
* Integrate maps in streamlit app with Folium, for God's sake, this is Carto! 


Manuel Cotallo
30/4/2021