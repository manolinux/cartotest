#Configuration class, all values are static


class Settings:

    functions  = ['avg','max','min']
    variables = ['so2','no2','co','o3','pm10','pm2_5','o3']
    seriesStep = ['hour','day','week','month','year']
    cartoUrl = "https://aasuero.carto.com:443/api/v2/sql?q="
    stationsUrl = cartoUrl + \
            "select {0} from aasuero.test_airquality_stations"
    observationsUrl = cartoUrl + \
            "select {0} from aasuero.test_airquality_measurements"
    observationsStatsUrl =  cartoUrl + \
            "select station_id,{0}({1}) as value,'{0}' as function,'{1}' as variable from aasuero.test_airquality_measurements"
    observationsTSeriesUrl = cartoUrl + \
            "select station_id,{0}({1}) as value,'{0}' as function,'{1}' as variable,date_trunc('{2}',timeinstant) as occurred_at from aasuero.test_airquality_measurements"
    stationsUrlPopulation = cartoUrl + \
            "select \'{0}\' as station_id,population from aasuero.esp_grid_1km_demographics where ST_Intersects(the_geom,cast(\'{1}\' as geometry))"
    geomIntersection = " where st_intersects(the_geom, ST_GeomFromGeoJSON({0})"
    notAvailablePopulation = -1
    intersectionFilter = '{"type":"Polygon","coordinates":[[[-3.63289587199688,40.56439731247202],[-3.661734983325005,40.55618117044514],[-3.66310827434063,40.53583209794804],[-3.6378740519285206,40.52421992151271],[-3.6148714274168015,40.5239589506112],[-3.60543005168438,40.547181381686634],[-3.63289587199688,40.56439731247202]]]}'
    stationsFilter = ['aq_jaen']
    
    #Endpoints
    baseUrl = "http://localhost:8000"
    endpoint1 = "{0}/stations/measure".format(baseUrl)
    endpoint2 = "{0}/stations/timeseries".format(baseUrl)
    endpoint3 = "{0}/stations".format(baseUrl)
    loginUrl = "{0}/login".format(baseUrl)
    logoutUrl = "{0}/logout".format(baseUrl)
    
    authSettings = {
        "authjwt_secret_key" : "secret",
        "authjwt_denylist_enabled"  : True,
        "authjwt_denylist_token_checks" : {"access"}
    }