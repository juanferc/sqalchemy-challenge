# Download dependencies
from datetime import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import numpy as np

# Create engine and set up connection to database

engine = create_engine("sqlite:///hawaii_3.db")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurements = Base.classes.measurements
Station = Base.classes.station

session=Session(engine)

# Set up Flask

app=Flask(__name__)

# Assign routes

@app.route("/")
def welcome():
    
    return (
        f"Avalable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations"
        f"//api/v1.0/tobs"
        f"/api/v1.0/calc_temps/<start>"
        f"/api/v1.0/calc_temps/<start>/<end>"
    )

# Precipiration route in JSON format

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    prcp_results = session.query(Measurements.date, Measurements.prcp).all()
    precipitation= []
    for result in prcp_results:
        row = {"date":"prcp"}
        row["date"] = result[0]
        row["prcp"] = float(result[1])
        precipitation.append(row)

    return jsonify(precipitation)

# Stations route in JSON format

@app.route("/api/v1.0/stations")
def stations():
   
    station_results = session.query(Station.station, Station.station_name).group_by(Station.station).all()

    station_list = list(np.ravel(station_results))
    return jsonify(station_list)

# Tobs and query dates route for the most active station for the last year of the data in Json format

@app.route("/api/v1.0/tobs")
def tobs():
    
    tobs_results = session.query(Measurements.station, Measurements.tobs).filter(Measurements.date.between("2016-08-01", "2017-08-01")).all()
    
    tobs_list=[]
    for tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["station"] = tobs[0]
        tobs_dict["tobs"] = float(tobs[1])
       
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

# Start date route to calculate minimum, maximum and average temperatures

def calc_temps(start="start_date"):

    start_date = datetime.strptime("2016-08-01", "%Y-%m-%d").date()
    start_results = session.query(func.max(Measurements.tobs), \
                            func.min(Measurements.tobs),\
                            func.avg(Measurements.tobs)).\
                            filter(Measurements.date >= start_date) 
    
    start_tobs = []
    for tobs in start_results:
        tobs_dict = {}
        tobs_dict["TAVG"] = float(tobs[2])
        tobs_dict["TMAX"] = float(tobs[0])
        tobs_dict["TMIN"] = float(tobs[1])
        
        start_tobs.append(tobs_dict)

    return jsonify(start_tobs)

# Route to calculate minimum, maximum and average temperatures between start and end dates

@app.route("/api/v1.0/calc_temps/<start>/<end>")

def calc_temps_2(start="start_date", end="end_date"): 

    start_date = datetime.strptime("2016-08-01", "%Y-%m-%d").date()
    end_date = datetime.strptime("2017-08-01", "%Y-%m-%d").date()

    start_end_results=session.query(func.max(Measurements.tobs).label("max_tobs"), \
                      func.min(Measurements.tobs).label("min_tobs"),\
                      func.avg(Measurements.tobs).label("avg_tobs")).\
                      filter(Measurements.date.between(start_date , end_date))   

    start_end_tobs = []
    for tobs in start_end_results:
        tobs_dict = {}
        tobs_dict["TAVG"] = float(tobs[2])
        tobs_dict["TMAX"] = float(tobs[0])
        tobs_dict["TMIN"] = float(tobs[1])

        start_end_tobs.append(tobs_dict)
        
    return jsonify(start_end_tobs)


if __name__ == "__main__":
        app.run(debug=True)



