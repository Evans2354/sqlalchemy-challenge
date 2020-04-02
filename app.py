# Modules
#====================================================
import numpy as np
import pandas as pd

import datetime as dt
from datetime import timedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func ,inspect,Table, Column, ForeignKey
from flask import Flask, jsonify
#========================================================
#connection setup
#========================================================

engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)



#======================================================
# Create app
#======================================================
app = Flask(__name__)

@app.route("/")
def Home():
    print("Server received request for 'Home' page...")
    return("<div ><p><h1> Welcome to the Climate App!</h1></p>"
  "<ul><li><strong>last 12 months rain data: </strong><font color='orange'> /api/v1.0/precipitation</font></li>"
           "<li><strong>List of station:</strong><font color='orange'> /api/v1.0/stations</font></li>"
           "<li><strong>Most active station for the last 12 Monthns:</strong><font color='orange'> /api/v1.0/tobs</font></li>"
           "<li><Strong>All dates greater than and equal to the start date: </strong><font color='orange'>/api/v1.0/&lt;start&gt;</font></li>"
            "<li><Strong>All dates between the start and end date inclusive: </strong><font color='orange'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</font></li></div>")
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return rain fall by date for the past one year"""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    N = 365
    date_365_days_ago = datetime.datetime.strptime(last_date,'%Y-%m-%d')  - timedelta(days=N)

    last_year_results_api = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= date_365_days_ago).all()
    results_df_api = pd.DataFrame(last_year_results_api, columns=['Date', 'Precipitation'])
    results_df_api=results_df_api.set_index("Date")
    rain_api_dict=results_df_api.to_dict()["Precipitation"]
    rain_api_dict
    return  jsonify(rain_api_dict)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route("/api/v1.0/stations")
def stations():
    stations_list = session.query(Station.name, Station.station)
    stations_df = pd.read_sql(stations_list.statement, stations_list.session.bind)
    stations_df = stations_df.to_dict()
    return jsonify(stations_df)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route("/api/v1.0/tobs")
def raintotals():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    N = 365
    date_365_days_ago = datetime.datetime.strptime(last_date,'%Y-%m-%d')  - timedelta(days=N)

    last_year_ls = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= date_365_days_ago).all()
    df = pd.DataFrame(last_year_ls)
    df = df.set_index("date")
    dict_df = df.to_dict()["tobs"]
    return jsonify(dict_df) 

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route("/api/v1.0/<start>")
def startdate(start):
        user_start_date = dt.datetime.strptime(start,'%Y-%m-%d')
        
        calc_results = session.query(func.min(Measurement.tobs),\
        func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >=user_start_date).all()

        result_dict=\
        ({"MinTemp": (calc_results[0][0]), "MaxTemp": (calc_results[0][1]), "AvgTemp": (calc_results[0][2])})
        return jsonify(result_dict)
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route("/api/v1.0/<start>/<end>")
def startEnddate(start,end):
        start_date = dt.datetime.strptime(start,'%Y-%m-%d')
        end_date =dt.datetime.strptime(end,'%Y-%m-%d')
        
        start_end_results = session.query(func.min(Measurement.tobs),\
        func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >=start_date).\
        filter(Measurement.date <=end_date).all()

        se_result_dict=\
        ({"MinTemp": (start_end_results[0][0]), "MaxTemp": (start_end_results[0][1]),\
         "AvgTemp": (start_end_results[0][2])})
        return jsonify(se_result_dict)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ == "__main__":
    app.run(debug=True)
        
        
        
        